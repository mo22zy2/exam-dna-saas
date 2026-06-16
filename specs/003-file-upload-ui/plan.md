# Implementation Plan: File Upload UI & Validation

**Branch**: `003-file-upload-ui` | **Date**: 2026-06-15 | **Spec**: `specs/003-file-upload-ui/spec.md`

**Input**: Feature specification from `specs/003-file-upload-ui/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Free-tier and paid users need to upload PDF files (up to 50 MB each) into the system, classified as either "Exam" or "Lecture". The feature provides a drag-and-drop upload page with client-side validation (file type via extension + content inspection, size limit), per-file progress indication, sequential upload queue for batch selections (max 10 per batch), auto-rename on duplicate filenames, and free-tier usage limit display ("3 of 3 files used"). Server-side enforcement via FastAPI ensures plan boundaries cannot be bypassed. Existing model stubs (`File`, `UploadSession`) need extension with user association and classification fields.

## Technical Context

**Language/Version**: Python 3.10+ (backend), TypeScript 5.x (frontend)

**Primary Dependencies**:
- Backend: FastAPI, SQLAlchemy, Alembic, python-multipart, aiofiles, Pillow (PDF inspection)
- Frontend: Next.js 14+ App Router, react-dropzone, file-type (client-side magic byte check)
- Queue: RQ (Redis) — for potential async PDF validation jobs

**Storage**: PostgreSQL (metadata), local filesystem (uploaded PDFs) — NEEDS CLARIFICATION: local path vs S3-compatible object storage for production

**Testing**: pytest (backend, with httpx TestClient), Vitest + React Testing Library (frontend)

**Target Platform**: Linux server (Docker), modern browsers (Chrome, Firefox, Safari, Edge)

**Project Type**: Web application — backend API (FastAPI) + frontend SPA (Next.js)

**Performance Goals**: Upload 10 MB file in under 30 seconds over broadband; progress updates every ≤2 seconds; file list refresh within 5 seconds post-upload

**Constraints**:
- 50 MB per-file hard limit (client + server enforced)
- PDF-only via extension + magic byte inspection
- Server-side plan limit enforcement (mandatory per constitution IV)
- Sequential batch upload (max 10 files per batch)
- Auto-rename on duplicate filenames with numeric suffix

**Scale/Scope**: Tens of users initially; free tier capped at 3 files; each file up to 50 MB

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|-----------|-------|--------|
| **I. Technology Stack** | FastAPI + SQLAlchemy + Next.js + Tailwind — followed | ✅ PASS |
| **II. LLM Abstraction** | Not applicable (no LLM calls in upload flow) | ✅ N/A |
| **III. Input Validation** | All upload endpoints MUST validate with Pydantic models | ✅ GATE — must verify in Phase 1 |
| **IV. Server-Side Enforcement** | Free-tier file count limit MUST be enforced server-side; frontend display is UX-only | ✅ GATE — must verify in Phase 1 |
| **V. Job Reliability & Retry** | Any async RQ jobs MUST log errors to `Job` table, support 3 retries, mark failed on exhaustion | ✅ GATE — if async validation is added |
| **Dev Constraint: Scoped Changes** | Upload feature must not refactor unrelated auth code | ✅ PASS |
| **Quality: Structured Logging** | All new modules MUST use project logging utility (not print) | ✅ GATE — must verify in Phase 1 |
| **Quality: Envelope Format** | API responses MUST use `{success, data, error}` envelope | ✅ GATE — must verify in Phase 1 |

## Project Structure

### Documentation (this feature)

```text
specs/003-file-upload-ui/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api-contracts.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
# Web application structure

backend/
└── api/
    ├── app/
    │   ├── upload/
    │   │   ├── __init__.py
    │   │   ├── router.py          # POST /upload, GET /upload/files, etc.
    │   │   ├── schemas.py         # Pydantic request/response models
    │   │   └── utils.py           # File storage, PDF inspection helpers
    │   ├── models/
    │   │   ├── file.py            # UPDATE: add user_id, classification fields
    │   │   └── upload_session.py  # UPDATE: add file_count tracking
    │   ├── main.py                # UPDATE: register upload router
    │   └── config.py              # UPDATE: add upload settings (storage path, limits)
    ├── alembic/
    │   └── versions/              # ADD: migration for file/upload_session changes
    └── requirements.txt           # UPDATE: add python-multipart, aiofiles

frontend/
└── web/
    ├── src/
    │   ├── app/
    │   │   ├── upload/
    │   │   │   └── page.tsx       # ADD: upload page
    │   │   └── layout.tsx         # UPDATE: add upload to nav
    │   ├── components/
    │   │   ├── FileDropzone.tsx   # ADD: drag & drop zone
    │   │   ├── FileList.tsx       # ADD: file list with progress
    │   │   ├── UploadQueue.tsx    # ADD: sequential queue display
    │   │   └── UsageLimitBadge.tsx# ADD: free-tier counter display
    │   └── lib/
    │       └── upload.ts          # ADD: upload API client + progress tracking
    └── package.json               # UPDATE: add react-dropzone
```

**Structure Decision**: Existing backend (`api/app/`) and frontend (`web/src/`) structure is maintained. New `upload/` module follows the same pattern as `auth/`. Existing model stubs (`File`, `UploadSession`) are extended rather than replaced.

## Complexity Tracking

No constitution violations detected. All design choices conform to the existing technology stack and patterns.
