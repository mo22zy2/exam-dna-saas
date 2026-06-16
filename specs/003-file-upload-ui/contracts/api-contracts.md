# API Contracts: File Upload

**Date**: 2026-06-15

All responses follow the envelope `{ "success": bool, "data": ..., "error": ... }`.

---

## POST /upload/session — Create Upload Session

Initiates a new upload session. Rejects if user already has an active session in "uploading" status.

**Request**: (no body — session starts empty)

**Response `201`**:
```json
{
  "success": true,
  "data": {
    "session_id": "uuid",
    "status": "pending",
    "file_count": 0,
    "max_files": 10
  }
}
```

**Response `409`**:
```json
{
  "success": false,
  "error": { "code": "ACTIVE_SESSION_EXISTS", "message": "An upload session is already in progress" }
}
```

---

## POST /upload/{session_id}/files — Upload Single File

Uploads one file within an active session. Must include classification tag. Sequential — only one file uploads at a time per session.

**Request**: `multipart/form-data`
- `file`: binary (PDF)
- `classification`: string ("exam" or "lecture")
- `client_upload_id`: UUID (client-generated for idempotency)

**Response `201`**:
```json
{
  "success": true,
  "data": {
    "file_id": "uuid",
    "filename": "report.pdf",
    "file_size": 1048576,
    "classification": "exam",
    "status": "uploaded",
    "created_at": "2026-06-15T12:00:00Z"
  }
}
```

**Response `400`** — Validation errors:
```json
{
  "success": false,
  "error": { "code": "INVALID_FILE_TYPE", "message": "Only PDF files are accepted" }
}
```

```json
{
  "success": false,
  "error": { "code": "FILE_TOO_LARGE", "message": "File exceeds 50 MB limit" }
}
```

```json
{
  "success": false,
  "error": { "code": "CLASSIFICATION_REQUIRED", "message": "Each file must be classified as 'exam' or 'lecture'" }
}
```

```json
{
  "success": false,
  "error": { "code": "PLAN_LIMIT_REACHED", "message": "You have reached your upload limit. Upgrade your plan to upload more files." }
}
```

---

## GET /upload/session/{session_id} — Get Session Status

Returns current session state including per-file statuses for the queue.

**Response `200`**:
```json
{
  "success": true,
  "data": {
    "session_id": "uuid",
    "status": "uploading",
    "files": [
      { "file_id": "uuid", "filename": "exam1.pdf", "file_size": 2048, "classification": "exam", "status": "completed", "progress": 100 },
      { "file_id": "uuid", "filename": "lecture1.pdf", "file_size": 1024, "classification": "lecture", "status": "uploading", "progress": 60 },
      { "file_id": null, "filename": "exam2.pdf", "file_size": 4096, "classification": "exam", "status": "pending", "progress": 0 }
    ]
  }
}
```

---

## GET /upload/files — List User's Uploaded Files

Returns all successfully uploaded files for the authenticated user.

**Response `200`**:
```json
{
  "success": true,
  "data": {
    "files": [
      { "file_id": "uuid", "filename": "exam1.pdf", "file_size": 2048, "classification": "exam", "created_at": "..." },
      { "file_id": "uuid", "filename": "lecture1.pdf", "file_size": 1024, "classification": "lecture", "created_at": "..." }
    ],
    "total_count": 2,
    "plan_limit": 3
  }
}
```

---

## GET /upload/files/{file_id}/download — Download File

Streams the original file content.

**Response `200`**: Binary PDF stream with `Content-Type: application/pdf` and `Content-Disposition: attachment; filename="..."`.

**Response `404`**: `{ "success": false, "error": { "code": "FILE_NOT_FOUND", "message": "File not found" } }`

---

## GET /upload/limits — Get Current Usage

Returns the user's current file count and plan limit.

**Response `200`**:
```json
{
  "success": true,
  "data": {
    "files_uploaded": 2,
    "plan_limit": 3
  }
}
```

---

## Error Codes Reference

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_FILE_TYPE` | 400 | Not a PDF (extension or content) |
| `FILE_TOO_LARGE` | 400 | Exceeds 50 MB |
| `CLASSIFICATION_REQUIRED` | 400 | Missing exam/lecture tag |
| `PLAN_LIMIT_REACHED` | 403 | User at their plan's file cap |
| `ACTIVE_SESSION_EXISTS` | 409 | Concurrent upload not allowed |
| `SESSION_NOT_FOUND` | 404 | Invalid session ID |
| `FILE_NOT_FOUND` | 404 | File ID not found or not owned by user |
| `SERVER_ERROR` | 500 | Unexpected failure |
