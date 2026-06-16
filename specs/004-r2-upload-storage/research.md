# Research: R2 Upload Storage

## Overview

Technology research and best-practice consolidation for the R2 upload storage feature. All NEEDS CLARIFICATION items from the Technical Context were resolved at plan authoring time; this document captures the rationale behind each technology choice.

---

## 1. Cloudflare R2 S3-Compatible Storage

### Decision
Use **boto3** (AWS SDK for Python) to interact with Cloudflare R2 via its S3-compatible API.

### Rationale
- R2 implements the S3 API, so boto3 works out of the box with a custom endpoint URL
- boto3 is the most widely used S3 SDK for Python, with extensive documentation and community support
- No vendor lock-in — switching to AWS S3 or another S3-compatible provider requires only an endpoint URL change

### Configuration
R2 requires four settings: `access_key_id`, `secret_access_key`, `bucket_name`, and `endpoint_url`. The endpoint URL format is:
```
https://<ACCOUNT_ID>.r2.cloudflarestorage.com
```
A `region` of `auto` is used for R2.

### Presigned URL Generation
- Use `boto3` client's `generate_presigned_url` method with `ClientMethod='put_object'`
- Expiration: 900 seconds (15 minutes) per spec
- The presigned URL allows PUT requests with the file body — no auth headers needed
- After the file is uploaded to R2, the server receives a callback or the client sends a completion notification

### Alternatives Considered
- **cloudflare-r2 package**: Third-party wrapper — less maintained than boto3, unnecessary abstraction
- **Direct HTTP upload to custom endpoint**: Would require implementing S3 signing manually — error-prone

---

## 2. Rate Limiting with slowapi

### Decision
Use **slowapi** middleware with per-user rate limiting keyed by authenticated user ID.

### Rationale
- slowapi integrates natively with FastAPI via middleware and dependency injection
- Supports per-user rate limits via custom key functions (extract `current_user.id` from request)
- Rate limit: `10/minute` per user
- Returns standard 429 status with Retry-After header

### Integration
- Add `@limiter.limit("10/minute")` to upload endpoints
- For unauthenticated requests, rate limit by IP (lower limit, e.g., `5/minute`)
- Exclude non-upload routes from rate limiting

### Alternatives Considered
- **Custom middleware**: More control but duplicates existing well-tested functionality
- **Redis-based rate limiting**: Overkill for single-server MVP without horizontal scaling

---

## 3. Magic Byte Validation with python-magic

### Decision
Use **python-magic** (libmagic bindings) for post-upload content type validation instead of the current simple `%PDF` header check.

### Rationale
- python-magic reads the actual file content signature, not just the first few bytes
- Detects true file type regardless of file extension or header spoofing
- More robust than checking `%PDF` header alone (PDF spec allows variations)
- Returns MIME type string (e.g., `application/pdf`) which can be stored in the `mime_type` field

### Integration
- Run validation in an async RQ job triggered after the file arrives in R2
- If MIME type is not `application/pdf`, mark file as `rejected` and notify user
- If valid, transition file state from `uploaded` → `validated` → `available`

### Alternatives Considered
- **Current `content.startswith(b"%PDF")` check**: Only checks first 4 bytes, trivially bypassed
- **pypdf attempt-parse**: Catches corruption but doesn't identify file type
- **file-type JavaScript library**: Client-side only, bypassable

---

## 4. Post-Upload Validation via RQ Jobs

### Decision
Use **RQ (Redis Queue)** for async post-upload content validation, matching the existing queue infrastructure.

### Rationale
- RQ is already the project's chosen queue (per constitution: "Celery and BullMQ MUST NOT be used")
- Validation is non-blocking — the presigned URL upload completes, then validation runs asynchronously
- Max 3 retries on failure, with error logging to the Job table (per Constitution V)
- The frontend polls file status or receives the result via the existing file list endpoint

### Flow
1. Client gets presigned URL → uploads directly to R2
2. Client calls server callback with `file_id` → server enqueues validation job
3. RQ job downloads file from R2 → runs python-magic → updates file state
4. Frontend polls file list → sees updated validation status

### Alternatives Considered
- **Synchronous validation**: Would defeat the purpose of direct browser upload (files would need to pass through the server)
- **R2 event notifications (webhooks)**: R2 doesn't support event notifications in the free tier
- **Polling from frontend**: Acceptable for MVP; server-sent events could be added later

---

## 5. File Lifecycle State Machine

### Decision
Four states with explicit transitions:

```
uploaded → validated → available
                       ↘ rejected
```

### Rationale
- `uploaded`: File is in R2 but not yet validated. Not usable for analysis.
- `validated`: Content check passed. Marks the file as ready.
- `available`: The file is fully processed and ready for analysis (implies validated).
- `rejected`: Content check failed. File stays in R2 but is quarantined (not visible for analysis).

### State persistence
- The `File` model's `status` field expands from a simple string to this state machine
- Add a `validation_status` field or repurpose existing `status` field (preferred to keep design minimal)

---

## 6. Upload Session Auto-Creation

### Decision
Replace the explicit `POST /upload/session` endpoint with automatic session creation on the first file upload.

### Rationale
- The spec (FR-006) requires: "create a session record when the first file in a logical upload flow is accepted"
- Simpler frontend flow — no need to create a session before uploading
- Session is created server-side when the first presigned URL is requested
- Session auto-closes after 30 minutes of inactivity (per clarification)

### Changes to existing code
- Remove or deprecate the existing `POST /upload/session` endpoint (from 003 feature)
- The presigned URL endpoint checks for an active session (open within 30 min); if none, creates one

---

## Summary of Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Storage backend | R2 via boto3 S3 API | No vendor lock-in, mature SDK |
| Presigned URL | boto3 `generate_presigned_url` | Built-in, 15 min expiry |
| Rate limiting | slowapi middleware | Native FastAPI integration |
| Content validation | python-magic (async RQ job) | Robust type detection, non-blocking |
| Async job queue | RQ (existing) | Matches project constitution |
| File states | uploaded → validated → available / rejected | Clear lifecycle for post-upload validation |
| Session creation | Auto-create on first file | Removes manual step, matches spec |
