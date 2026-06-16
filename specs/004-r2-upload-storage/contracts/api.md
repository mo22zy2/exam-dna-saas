# API Contracts: R2 Upload Storage

Base URL: `http://localhost:8000` (dev)  
All endpoints prefixed with `/upload` (existing).  
Auth: JWT in httpOnly cookie (existing auth system).

---

## POST /upload/presign-url

Generate a presigned URL for direct browser upload to R2. Auto-creates or reuses an open UploadSession.

**Auth**: Required (authenticated user)

**Request body**:
```json
{
  "filename": "exam-2026.pdf",
  "file_size": 245000,
  "classification": "exam"
}
```

| Field | Type | Constraints |
|-------|------|-------------|
| `filename` | string | 1–255 chars |
| `file_size` | integer | Must be ≤ 50 MB |
| `classification` | string | Must be "exam" or "lecture" (from existing 003 feature) |

**Server-side checks** (before issuing URL):
1. Rate limit: max 10 requests/min per user (slowapi) ← **NEW**
2. Free tier: user must have < 20 stored files (FR-003)
3. Analysis quota: user must have < 1 analysis this month (FR-004)

**Success response (200)**:
```json
{
  "success": true,
  "data": {
    "presigned_url": "https://<bucket>.r2.cloudflarestorage.com/users/{user_id}/{file_id}.pdf?X-Amz-Algorithm=...&X-Amz-Expires=900",
    "file_id": "uuid-string",
    "session_id": "uuid-string",
    "expires_in_seconds": 900
  }
}
```

**Error responses**:
```json
// 429 - Rate limit exceeded
{"success": false, "error": {"code": "RATE_LIMITED", "message": "Too many uploads. Try again in 60 seconds."}}

// 403 - Plan limit reached
{"success": false, "error": {"code": "PLAN_LIMIT_REACHED", "message": "You have reached your limit of 20 stored files."}}

// 403 - Analysis quota exceeded
{"success": false, "error": {"code": "ANALYSIS_QUOTA_EXCEEDED", "message": "Monthly analysis quota (1) exhausted."}}
```

---

## POST /upload/{file_id}/complete

Notify server that a direct upload to R2 is complete. Triggers post-upload content validation.

**Auth**: Required (authenticated user)

**Path params**: `file_id` — UUID returned from presign-url endpoint

**Request body**: (empty/optional — could carry client-side metadata if needed)

**Success response (200)**:
```json
{
  "success": true,
  "data": {
    "file_id": "uuid-string",
    "status": "uploaded",
    "validation_status": "pending"
  }
}
```

---

## GET /upload/files (existing, extended)

List the authenticated user's uploaded files.

**Auth**: Required

**Query params**: (none in MVP — future: pagination, filter)

**Success response (200)**:
```json
{
  "success": true,
  "data": {
    "files": [
      {
        "file_id": "uuid",
        "filename": "exam.pdf",
        "file_size": 245000,
        "classification": "exam",
        "status": "uploaded",
        "validation_status": "validated",
        "session_id": "uuid",
        "created_at": "2026-06-16T12:00:00Z"
      }
    ],
    "total_count": 5,
    "plan_limit": 20
  }
}
```

**Changes from existing**: Added `validation_status` and `session_id` to `FileListItem`.

---

## GET /upload/limits (existing)

Return current user's upload and analysis usage against plan limits.

**Auth**: Required

**Success response (200)**:
```json
{
  "success": true,
  "data": {
    "files_uploaded": 3,
    "files_limit": 20,
    "analyses_used": 0,
    "analyses_limit": 1
  }
}
```

**Changes from existing**: Added `analyses_used` and `analyses_limit`.

---

## Rate Limit Headers

All `/upload/*` endpoints include rate limit headers on response:

| Header | Example | Description |
|--------|---------|-------------|
| `X-RateLimit-Limit` | `10` | Max requests per window |
| `X-RateLimit-Remaining` | `7` | Requests left in current window |
| `X-RateLimit-Reset` | `1623849600` | Unix timestamp when window resets |

On 429 response, the `Retry-After` header indicates seconds to wait.

---

## Error Envelope (existing pattern)

All errors follow the existing `{success, data, error}` envelope:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description"
  }
}
```
