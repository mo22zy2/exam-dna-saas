# Quickstart: R2 Upload Storage Validation

## Prerequisites

- Docker: Postgres 16 + Redis 7 running via `docker compose up -d`
- Backend running: `cd api && .venv\Scripts\Activate.ps1 && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- Frontend running: `cd web && npm run dev` (uses `--webpack` flag as needed)
- Cloudflare R2 bucket created and credentials in `api/.env`
- Dependencies installed: `pip install boto3 python-magic python-magic-bin slowapi`

## Validation Scenarios

### Scenario 1: Generate a Presigned URL

```bash
# Authenticate first
curl -X POST http://localhost:8000/auth/jwt/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=secret" \
  -c cookies.txt

# Request presigned URL
curl -X POST http://localhost:8000/upload/presign-url \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"filename": "test-exam.pdf", "file_size": 102400, "classification": "exam"}'
```

**Expected outcome**: 200 response with `presigned_url`, `file_id`, `session_id`, `expires_in_seconds: 900`.

---

### Scenario 2: Upload File Directly to R2

```bash
# Get a presigned URL first (from Scenario 1), then:
curl -X PUT "<presigned_url>" \
  -H "Content-Type: application/pdf" \
  --data-binary "@test-exam.pdf"
```

**Expected outcome**: 200 from R2 (file stored). No error.

---

### Scenario 3: Complete Upload and Trigger Validation

```bash
# Use the file_id from Scenario 1
curl -X POST http://localhost:8000/upload/<file_id>/complete \
  -b cookies.txt
```

**Expected outcome**: 200 response with `status: "uploaded"`, `validation_status: "pending"`.  
After a few seconds (RQ job runs): file status transitions to `validated` or `rejected`.

---

### Scenario 4: Verify Rate Limiting

```bash
# Send 11 requests rapidly
for ($i=0; $i -le 10; $i++) {
  curl -X POST http://localhost:8000/upload/presign-url \
    -H "Content-Type: application/json" \
    -b cookies.txt \
    -d '{"filename": "test.pdf", "file_size": 100, "classification": "exam"}'
}
```

**Expected outcome**: First 10 requests succeed (200), 11th returns 429 with `RATE_LIMITED` error code and `Retry-After` header.

---

### Scenario 5: Verify Free Tier File Limit

1. Upload 20 valid files (repeat Scenarios 1-3 with different filenames)
2. Attempt to upload file #21

**Expected outcome**: Upload #21 returns 403 with `PLAN_LIMIT_REACHED` error.

---

### Scenario 6: Verify Monthly Analysis Quota

1. Upload a file successfully
2. This feature only *checks* the analysis counter; incrementing it belongs to the analysis feature
3. When `analyses_count` for current month ≥ 1, presign-url returns 403 with `ANALYSIS_QUOTA_EXCEEDED`

---

### Scenario 7: Verify Unauthenticated Rejection

```bash
curl -X POST http://localhost:8000/upload/presign-url \
  -H "Content-Type: application/json" \
  -d '{"filename": "test.pdf", "file_size": 100, "classification": "exam"}'
```

**Expected outcome**: 401 unauthorized.

---

### Scenario 8: Verify Presigned URL Expiry

1. Get a presigned URL
2. Wait 15+ minutes
3. Attempt to PUT a file using the expired URL

**Expected outcome**: R2 returns 403 (ExpiredToken).

---

### Scenario 9: File List with Validation Status

```bash
curl -X GET http://localhost:8000/upload/files -b cookies.txt
```

**Expected outcome**: 200 response with files array, each entry including `validation_status` and `session_id` fields.

---

## Quick Test Script

Save as `test-r2-upload.sh` (or `.ps1` for PowerShell):

```bash
# PowerShell version
$email = "test@example.com"
$password = "testpass123"
$base = "http://localhost:8000"

# Login
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest -Uri "$base/auth/jwt/login" -Method Post `
  -Body "username=$email&password=$password" `
  -ContentType "application/x-www-form-urlencoded" `
  -WebSession $session | Out-Null

# Request presigned URL
$resp = Invoke-RestMethod -Uri "$base/upload/presign-url" -Method Post `
  -Body (ConvertTo-Json @{filename="test.pdf"; file_size=51200; classification="exam"}) `
  -ContentType "application/json" `
  -WebSession $session

Write-Host "Presigned URL: $($resp.data.presigned_url)"
Write-Host "File ID: $($resp.data.file_id)"

# Upload directly to R2
Invoke-RestMethod -Uri $resp.data.presigned_url -Method Put `
  -ContentType "application/pdf" `
  -InFile "test.pdf"

# Complete upload
Invoke-RestMethod -Uri "$base/upload/$($resp.data.file_id)/complete" -Method Post `
  -WebSession $session

# List files
$files = Invoke-RestMethod -Uri "$base/upload/files" -Method Get `
  -WebSession $session
Write-Host "Files: $($files.data.files.Count) total"
```

## Expected Outcomes Summary

| Scenario | Endpoint | Expected HTTP | Key Assertion |
|----------|----------|---------------|---------------|
| Presigned URL | POST /upload/presign-url | 200 | URL contains X-Amz-Expires=900 |
| Direct upload | PUT (R2 URL) | 200 | File in R2 bucket |
| Complete + validate | POST /upload/{id}/complete | 200 | status=uploaded |
| Rate limit | POST /upload/presign-url × 11 | 429 (11th) | Retry-After header |
| File limit | 21st upload | 403 | PLAN_LIMIT_REACHED |
| Analysis quota | After 1 analysis | 403 | ANALYSIS_QUOTA_EXCEEDED |
| Unauthenticated | POST /upload/presign-url | 401 | No session |
| Expired URL | PUT (after 15 min) | 403 | ExpiredToken |
| File list | GET /upload/files | 200 | validation_status present |
