# Research: File Upload UI & Validation

**Date**: 2026-06-15

## Resolved Clarifications

### File Storage Backend (Local vs S3-Compatible)

- **Decision**: Local filesystem for development; abstracted storage interface for future S3 swap
- **Rationale**: The project currently has no cloud infrastructure provisioned. Using a `StorageBackend` abstraction with a local `LocalStorageBackend` implementation allows straightforward future migration to S3/MinIO without changing business logic. Files stored under `api/uploads/` organized by `{user_id}/{file_id}.pdf`.
- **Alternatives considered**: S3 directly (infrastructure overhead for dev), database BLOBs (poor performance for large files, complicates backups)

### Server-Side PDF Validation Strategy

- **Decision**: Inspect PDF magic bytes (`%PDF` header at offset 0) + attempt PyPDF2/`pypdf` open as a secondary validation
- **Rationale**: Magic byte check rejects non-PDF content quickly without heavy processing. PyPDF2 open provides defense-in-depth by attempting actual PDF parsing. Both checks run server-side before storing the file.
- **Alternatives considered**: pdfplumber (heavier), custom magic byte only (bypassable with header-only fakes)

### File Serving Mechanism

- **Decision**: Direct file download via FastAPI streaming endpoint (`GET /upload/files/{file_id}/download`) — no signed URLs
- **Rationale**: For the current scale (tens of users), a simple streaming response is sufficient. The storage abstraction makes switching to presigned URLs trivial if S3 is adopted later.
- **Alternatives considered**: Presigned URLs (infrastructure dependency), static file serving via nginx (adds deployment complexity)

### Upload ID Generation and Idempotency

- **Decision**: Client generates a temporary `client_upload_id` (UUIDv4) per file before upload to enable idempotent retry on network failure
- **Rationale**: If a file upload is interrupted, the retry with the same `client_upload_id` allows the server to resume or deduplicate rather than creating orphaned partial files.
- **Alternatives considered**: Server-generated IDs (no retry safety), content-hash dedup (overkill for v1)

### Free-Tier Limit Enforcement

- **Decision**: Check file count on `User` model (existing `analyses_used_this_month` pattern — add `files_uploaded` counter)
- **Rationale**: Follows the existing project pattern for plan-based limits (`User.analyses_used_this_month`). A `files_uploaded` integer column on `User` is incremented on successful upload and used as the server-side gate.
- **Alternatives considered**: Separate `Usage` table (more flexible but overengineered for current scale), counting `File` rows per user at request time (adds query overhead on every upload)

### Concurrent Upload Guard

- **Decision**: Limit to 1 active upload session per user at a time; reject new upload if a session is already in "uploading" status
- **Rationale**: Prevents accidental concurrent uploads that could exceed the sequential queue limit and simplifies server-side state management.
- **Alternatives considered**: Allow multiple sessions (unnecessary complexity for sequential queue model)
