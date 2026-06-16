# Quickstart: File Upload

**Date**: 2026-06-15

## Prerequisites

- Docker containers running: `docker compose up -d` (Postgres 16 + Redis 7)
- Backend running: `uvicorn app.main:app --reload` from `api/`
- Frontend running: `npm run dev -- --webpack` from `web/`
- Existing user account (create via `/register` or `/login`)

## Validation Scenarios

### 1. Single PDF Upload

1. Log in at `http://localhost:3000/login`
2. Navigate to upload page (`http://localhost:3000/upload`)
3. Drag a valid PDF file (~1 MB) into the dropzone
4. Select "Exam" classification
5. Click Upload
6. **Expected**: Progress bar advances, file appears in list with "Exam" tag

### 2. PDF Rejection (Magic Byte Check)

1. Create a file named `fake.pdf` containing only text "This is not a PDF"
2. Drag it into the dropzone
3. **Expected**: Immediate rejection with "Only PDF files are accepted"

### 3. Size Limit Enforcement

1. Create/locate a file larger than 50 MB
2. Drag into dropzone
3. **Expected**: Rejection with "File exceeds 50 MB limit"

### 4. Free-Tier Limit

1. Log in as a free-tier user with 3 files already uploaded (or upload 3 files)
2. Try to upload a 4th file
3. **Expected**: Rejection with "You have reached your upload limit"

### 5. Sequential Batch Upload (10 File Cap)

1. Select 10 valid PDFs with various classifications
2. Click Upload
3. **Expected**: Files upload one at a time (sequentially), queue shows pending/uploading/completed states
4. Select an 11th file
5. **Expected**: 11th file is ignored with a notification (cap at 10)

### 6. Auto-Rename on Duplicate

1. Upload `report.pdf`
2. Upload another `report.pdf`
3. **Expected**: Second file stored as `report (1).pdf`; both appear with original name "report.pdf" in the file list

### 7. API-Only: Server-Side Enforcement

1. Use curl/Postman to send a POST request to `/upload/files` without an auth cookie
   ```bash
   curl -X POST http://localhost:8000/upload/files -F "file=@test.pdf"
   ```
2. **Expected**: `401 Unauthorized`

## Commands

```bash
# Backend tests
cd api
pytest tests/upload/ -v

# Frontend tests
cd web
npx vitest run src/app/upload/
```
