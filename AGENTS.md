<!-- SPECKIT START -->
The current implementation plan is at `specs/004-r2-upload-storage/plan.md`.
Read it for project structure, tech stack, and design decisions.
<!-- SPECKIT END -->

## Session Context (2026-06-16)

### Status
- **All 33 auth tasks COMPLETE** — master branch, commit `72e3c33`
- **Spec 004 (R2 upload storage) COMPLETE** — all 30 tasks done
- Docker: Postgres 16 + Redis 7 running via `docker compose up -d`
- Backend: uvicorn on `http://0.0.0.0:8000` (run from `api/`)
- Frontend: Next.js on `http://localhost:3000` (use `--webpack` flag)
- Google OAuth credentials set in `api/.env` by user

### What's built (Auth — Spec 003)
- Backend: `POST /auth/register`, `POST /auth/jwt/login`, `POST /auth/logout`, `GET /auth/google`, `GET /auth/google/callback`, `GET /auth/me`, `GET /health`
- Frontend: `/login` (email/pw + Google button), `/register`, `/profile` (protected), `/` (dashboard), Header with user menu + sign out
- Auth: JWT in httpOnly cookie, bcrypt passwords, Google OAuth via httpx-oauth, OAuthIdentity model with UniqueConstraint

### What's built (Upload Storage — Spec 004)
- **Storage**: `LocalStorageBackend` (default, no R2). Presigned URLs point to `PUT /upload/storage/{key}` on app server.
- **Endpoints**: `POST /upload/presign-url` (rate-limited, quota-enforced), `PUT /upload/storage/{key}` (receives file bytes), `POST /upload/{file_id}/complete` (triggers async validation), `GET /upload/files` (with `validation_status` + `session_id`), `GET /upload/limits` (with `analyses_used` + `analyses_limit`). Old `POST /upload/{session_id}/files` deprecated.
- **Validation**: Post-upload async RQ job using `python-magic` (PDF MIME check, not PyPDF reader). `validation_status` on File model (`pending` → `validated`/`rejected`).
- **Sessions**: Auto-created on first presign-url call, auto-closed after 30min inactivity (`last_activity` column). `SELECT ... FOR UPDATE` on quota checks.
- **Rate Limiting**: slowapi, 10 uploads/min per user, cookie-based key.
- **Free Tier**: 20 stored files, 1 analysis/month capped at server side.
- **Frontend**: `upload.ts` client — `uploadFileViaPresignedUrl()` with 2-retry on 403, `<50MB check`.

### Files to know
- `api/app/auth/router.py` — all auth endpoints
- `api/app/upload/router.py` — all upload endpoints (presign, complete, local storage, lists, limits)
- `api/app/upload/utils.py` — StorageBackend ABC, LocalStorageBackend, R2StorageBackend, `generate_presigned_upload_url()`, `validate_pdf_content()` (python-magic)
- `api/app/upload/validation.py` — `enqueue_content_validation()` + RQ job `validate_file_content()` (3 retries)
- `api/app/upload/schemas.py` — Pydantic models for upload flow
- `api/app/rate_limit.py` — shared slowapi Limiter instance
- `api/app/config.py` — Settings: `app_url`, free tier limits, R2 credentials
- `api/app/models/file.py` — File model with `validation_status`
- `api/app/models/upload_session.py` — UploadSession model with `last_activity`
- `web/src/lib/upload.ts` — Presigned URL client functions
- `web/src/app/upload/page.tsx` — Upload page with presigned URL flow
- `web/src/lib/auth.tsx` — AuthProvider + useAuth() hook
- `web/src/app/login/page.tsx` — login form + Google button
- `web/src/app/page.tsx` — dashboard (authed) / redirect (unauthed)
- `web/src/app/profile/page.tsx` — profile page wrapped in ProtectedLayout
- `web/src/components/Header.tsx` — header with email + sign out
- `web/src/components/ProtectedLayout.tsx` — route guard

### Next possible work
- Email verification (deferred)
- Password reset (out of scope)
- Production deployment prep
