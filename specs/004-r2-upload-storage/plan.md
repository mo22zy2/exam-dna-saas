# Implementation Plan: R2 Upload Storage

**Branch**: `004-r2-upload-storage` | **Date**: 2026-06-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/004-r2-upload-storage/spec.md`

## Summary

Replace the existing local-filesystem storage backend with Cloudflare R2 (S3-compatible) for file uploads, add presigned URL generation for direct browser uploads, enforce rate limiting (10 uploads/min per user), upgrade magic byte validation to use python-magic, add file lifecycle state tracking, auto-create upload sessions, and enforce the monthly analysis quota (1/month) on top of the existing 20-file free tier limit. The existing upload router and model stubs from 003-file-upload-ui will be extended — not replaced.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5.x (frontend)

**Primary Dependencies**:
  - Backend: FastAPI, SQLAlchemy 2.0, Alembic, boto3 (R2 S3 client), python-magic (content inspection), slowapi (rate limiting), httpx-oauth (existing)
  - Frontend: Next.js 14+ (App Router), TypeScript, Tailwind CSS, existing upload components
  - Queue: RQ (Redis) — if async post-upload validation is needed

**Storage**: PostgreSQL (user data, file metadata, quotas, sessions); Cloudflare R2 (file binaries, S3-compatible via boto3)

**Testing**: pytest + pytest-asyncio (backend API tests); vitest (frontend component tests)

**Target Platform**: Linux Docker container (deployed), Windows/macOS (local dev via docker compose)

**Project Type**: Web application — backend API (FastAPI) + frontend (Next.js)

**Performance Goals**: Upload tokens issued in <500ms; rate limit window accurate to the second; post-upload validation completes within 30s of upload notification

**Constraints**: Rate limit: 10 upload attempts/min per user; presigned URLs expire in 15 min; upload session auto-closes after 30 min inactivity; free tier: 20 stored files max, 1 analysis/month

**Scale/Scope**: Single-server MVP; auth for user identification already exists

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Rationale |
|-----------|--------|-----------|
| I. Technology Stack | **PASS** | Backend is Python/FastAPI + SQLAlchemy — this feature extends the existing `upload/` module following the same pattern as `auth/`. No Prisma, no Celery, no BullMQ. |
| II. LLM Abstraction Layer | **PASS** (N/A) | This feature does not invoke any LLM provider. No calls to `llm.py` needed. |
| III. Input Validation | **PASS** | All new and modified endpoints will use Pydantic request/response models (following existing schemas in `upload/schemas.py`). Structured error responses match the existing `{success, data, error}` envelope. |
| IV. Server-Side Enforcement | **PASS** | Rate limiting (slowapi), free-tier quotas (20 files, 1 analysis/month), and post-upload content validation are all enforced server-side. No client-only checks. |
| V. Job Reliability & Retry | **PASS** | Post-upload content validation and any async RQ jobs will log errors to the Job table with max 3 retries, matching existing patterns. |
| Development Constraints | **PASS** | Changes scoped to `api/app/upload/`, `api/app/models/`, and config. No unrelated refactoring. |
| Quality & Observability | **PASS** | Structured logging via `logging.getLogger` (existing pattern). API responses follow `{success, data, error}` envelope. Expected vs unexpected errors distinguished. |

**GATE verdict**: All 8 gates pass. No violations requiring Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/004-r2-upload-storage/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
api/
├── app/
│   ├── config.py                        # [+R2 settings, rate limit settings]
│   ├── main.py                          # [+slowapi middleware, +upload router prefix fix]
│   ├── upload/
│   │   ├── __init__.py
│   │   ├── router.py                    # [MODIFY: add presigned URL endpoint, auto-create session, remove explicit POST /session]
│   │   ├── schemas.py                   # [+PresignedUrlResponse, +extend FileListItem with validation_status]
│   │   ├── utils.py                     # [+R2StorageBackend, +python-magic validation, +presigned URL generation]
│   │   └── validation.py                # [NEW: post-upload content validation job logic]
│   ├── models/
│   │   ├── file.py                      # [+validation_status field, +lifecycle state enum]
│   │   └── upload_session.py            # [+last_activity field, +auto-close logic]
│   └── auth/                            # (unchanged)
├── alembic/                             # [+migration: add columns to files, upload_sessions]
│   └── versions/
├── requirements.txt                     # [+boto3, +python-magic, +slowapi]
└── tests/
    └── upload/                          # [NEW: upload endpoint tests]
        ├── conftest.py
        ├── test_upload.py
        └── test_rate_limit.py

web/
├── src/
│   ├── app/
│   │   └── upload/
│   │       └── page.tsx                 # [MODIFY: use presigned URL flow instead of server-proxy upload]
│   └── lib/
│       └── upload.ts                    # [MODIFY: presigned URL client logic]
```

**Structure Decision**: Web application with separate `api/` (FastAPI backend) and `web/` (Next.js frontend) — matching the existing pattern. All upload backend logic lives in `api/app/upload/` following the same module layout as `api/app/auth/`. Model stubs in `api/app/models/` are extended, not replaced. The frontend changes are minimal since the 003 feature already has the upload UI; only the upload transport (server-proxy → presigned URL) needs updating.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. Table omitted.

