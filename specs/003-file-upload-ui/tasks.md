# Tasks: File Upload UI & Validation

**Input**: Design documents from `specs/003-file-upload-ui/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-contracts.md, quickstart.md

**Tests**: Not requested in this iteration — focus on implementation only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `api/app/`
- **Frontend**: `web/src/`
- Paths adjusted based on plan.md structure (web application: backend + frontend)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and configure settings for file upload.

- [x] T001 Install `python-multipart`, `aiofiles`, and `pypdf` to `api/requirements.txt`
- [x] T002 [P] Install `react-dropzone` to `web/package.json`
- [x] T003 [P] Add upload storage path and file size limit settings to `api/app/config.py`
- [x] T004 [P] Create `api/app/upload/` package with `__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Data model updates, storage abstraction, and shared utilities that ALL user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T005 Add `user_id` (FK to users.id), `classification` (VARCHAR 20), `mime_type` (VARCHAR 50), `status` (VARCHAR 20), and `updated_at` columns to File model in `api/app/models/file.py`
- [x] T006 [P] Add `file_count` (INTEGER, default 0) column to UploadSession model in `api/app/models/upload_session.py`
- [x] T007 [P] Add `files_uploaded` (INTEGER, default 0) column to User model in `api/app/models/user.py`
- [x] T008 [P] Add `files` relationship to User model in `api/app/models/user.py`
- [x] T009 Update models `__init__.py` in `api/app/models/__init__.py`
- [x] T010 [P] Create `StorageBackend` abstract class and `LocalStorageBackend` implementation in `api/app/upload/utils.py`
- [x] T011 [P] Create PDF validation helper (magic byte check + pypdf parse) in `api/app/upload/utils.py`
- [x] T012 [P] Create upload schemas (request/response models) in `api/app/upload/schemas.py`
- [x] T013 Generate Alembic migration for File, UploadSession, and User model changes in `api/alembic/versions/003_add_upload_fields.py`

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Upload a PDF with Classification (Priority: P1) 🎯 MVP

**Goal**: A user can select up to 10 PDF files, assign an Exam/Lecture tag to each, and upload them sequentially with progress feedback.

**Independent Test**: Navigate to `/upload`, select a valid PDF under 50 MB, pick "Exam" classification, click upload — confirm progress bar advances and file appears in the list with correct tag.

### Backend Implementation for User Story 1

- [x] T014 [P] [US1] Create UploadSession creation endpoint (`POST /upload/session`) in `api/app/upload/router.py` — returns session_id, enforces single active session per user
- [x] T015 [P] [US1] Create Pydantic request/response schemas for upload in `api/app/upload/schemas.py` — `UploadSessionResponse`, `FileUploadResponse`, `FileDetail`
- [x] T016 [US1] Implement single file upload endpoint (`POST /upload/{session_id}/files`) in `api/app/upload/router.py` — validates PDF type (magic bytes + pypdf), size (50 MB), classification, plan limit; stores file via StorageBackend; creates File record; increments `User.files_uploaded`
- [x] T017 [US1] Add Pydantic validation models for upload request (multipart file + classification field) in `api/app/upload/schemas.py`
- [x] T018 [US1] Implement session status endpoint (`GET /upload/session/{session_id}`) returning per-file queue status in `api/app/upload/router.py`
- [x] T019 [US1] Add structured logging to all upload endpoints in `api/app/upload/router.py`
- [x] T020 [US1] Register upload router in `api/app/main.py`

### Frontend Implementation for User Story 1

- [x] T021 [P] [US1] Create upload API client (`createSession`, `uploadFile`, `getSessionStatus`) in `web/src/lib/upload.ts`
- [x] T022 [P] [US1] Create `FileDropzone` component (drag & drop area, PDF + size validation, file selection) in `web/src/components/FileDropzone.tsx`
- [x] T023 [P] [US1] Create `UploadQueue` component (sequential queue display with per-file status badges and progress bar) in `web/src/components/UploadQueue.tsx`
- [x] T024 [US1] Create upload page at `web/src/app/upload/page.tsx` integrating FileDropzone, classification selector, UploadQueue, and the upload flow logic

**Checkpoint**: At this point, User Story 1 should be fully functional — users can upload single and batch PDFs with progress and classification.

---

## Phase 4: User Story 2 - Understand Free-Tier Limits (Priority: P2)

**Goal**: A free-tier user can see their current file count and plan limit on the upload page. Server-side enforcement prevents exceeding the limit.

**Independent Test**: Log in as a free-tier user, verify "0 of 3 files used" is shown, upload 3 files, verify "3 of 3 files used", try uploading a 4th file — confirm it is rejected with a limit message.

### Backend Implementation for User Story 2

- [x] T025 [P] [US2] Create usage/limits endpoint (`GET /upload/limits`) returning `files_uploaded` and `plan_limit` in `api/app/upload/router.py`
- [x] T026 [US2] Integrate plan limit check into file upload endpoint (T016) — reject with `PLAN_LIMIT_REACHED` error if `User.files_uploaded >= plan_limit`
- [ ] T027 [US2] Add server-side enforcement tests via curl/httpx to validate limit cannot be bypassed (use existing plan_limit from User model)

### Frontend Implementation for User Story 2

- [x] T028 [P] [US2] Create `UsageLimitBadge` component (displays "X of Y files used") in `web/src/components/UsageLimitBadge.tsx`
- [x] T029 [US2] Integrate UsageLimitBadge into upload page and wire up to `/upload/limits` endpoint; update badge after each successful upload
- [x] T030 [US2] Handle `PLAN_LIMIT_REACHED` error in upload API client — show inline error message on upload page

**Checkpoint**: At this point, User Story 1 AND 2 both work — users see their limit and cannot exceed it.

---

## Phase 5: User Story 3 - View and Manage Uploaded Files (Priority: P3)

**Goal**: A user can see a list of all their uploaded files with name, size, and classification tag.

**Independent Test**: Upload two files (one Exam, one Lecture), navigate to upload page, confirm both appear in the file list with correct metadata; user with no files sees empty state message.

### Backend Implementation for User Story 3

- [x] T031 [P] [US3] Create file listing endpoint (`GET /upload/files`) returning all user's uploaded files in `api/app/upload/router.py`
- [x] T032 [P] [US3] Create file download endpoint (`GET /upload/files/{file_id}/download`) streaming file content in `api/app/upload/router.py`

### Frontend Implementation for User Story 3

- [x] T033 [P] [US3] Create `FileList` component (displays filename, size in human-readable format, classification tag, empty state) in `web/src/components/FileList.tsx`
- [x] T034 [P] [US3] Add `listFiles`, `downloadFile` functions to upload API client in `web/src/lib/upload.ts`
- [x] T035 [US3] Integrate FileList into upload page below the dropzone; refresh list after each successful upload

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories.

- [ ] T036 [P] Add error boundary and toast notification system for upload failures in `web/src/app/upload/page.tsx`
- [ ] T037 [P] Run Alembic migration on Docker Postgres and verify model state (requires `docker compose up -d`)
- [x] T038 Add upload link to navigation (Header component) in `web/src/components/Header.tsx`
- [x] T039 [P] Add logging configuration for upload module in `api/app/upload/__init__.py`
- [ ] T040 Run `quickstart.md` validation scenarios to confirm end-to-end flow

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - US3 (Phase 5) depends on US1 (Phase 3) for the upload infrastructure
  - US2 (Phase 4) can start in parallel with US1 after Foundational
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) — Depends on US1 endpoints for limit enforcement integration
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) — Depends on US1 upload infrastructure and File model

### Within Each User Story

- Models before services
- Services before endpoints
- Backend endpoints before frontend integration
- Frontend components can be built in parallel with backend
- Story complete before moving to next priority

### Parallel Opportunities

- T002, T003, T004 (all Setup [P]) can run in parallel
- T006, T007, T008, T010, T011, T012 (all Foundational [P]) can run in parallel
- T014, T015 (US1 backend schemas + session endpoint) can run in parallel
- T021, T022, T023 (US1 frontend components) can run in parallel
- T025, T028 (US2 backend + frontend) can run in parallel
- T031, T032, T033, T034 (US3 backend + frontend) can run in parallel
- T036, T037, T039 (Polish [P]) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all backend US1 tasks together:
Task: "Create UploadSession endpoint in api/app/upload/router.py" (T014)
Task: "Create Pydantic schemas in api/app/upload/schemas.py" (T015)

# Launch all frontend US1 tasks together:
Task: "Create upload API client in web/src/lib/upload.ts" (T021)
Task: "Create FileDropzone in web/src/components/FileDropzone.tsx" (T022)
Task: "Create UploadQueue in web/src/components/UploadQueue.tsx" (T023)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T013)
3. Complete Phase 3: User Story 1 (T014-T024)
4. **STOP and VALIDATE**: Test User Story 1 independently — select a PDF, upload it, see it in the list
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (upload with classification) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (free-tier limits) → Test independently → Deploy/Demo
4. Add User Story 3 (file list + download) → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:
1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 backend (T014-T020)
   - Developer B: User Story 1 frontend (T021-T024)
   - Both integrate at the end of Phase 3
3. Then:
   - Developer A: User Story 2 (T025-T027)
   - Developer B: User Story 3 (T031-T032) + User Story 2 frontend (T028-T030)
4. Final integration and polish together

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify migration runs clean before testing upload endpoints
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
