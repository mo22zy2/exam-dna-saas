---
description: "Task list for R2 Upload Storage feature"
---

# Tasks: R2 Upload Storage

**Input**: Design documents from `specs/004-r2-upload-storage/`

**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: No explicit test tasks — validation is handled by quickstart.md scenarios. Manual verification per user story independent test.

**Organization**: Tasks grouped by user story. Each story is independently implementable and testable.

**Note**: This feature EXTENDS the existing upload infrastructure built by 003-file-upload-ui (router, models, storage backend, frontend). Tasks are additive/modifying, not greenfield.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `api/app/upload/`, `api/app/models/`
- **Frontend**: `web/src/app/upload/`, `web/src/lib/`, `web/src/components/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and configure environment variables

- [ ] T001 Add boto3, python-magic, python-magic-bin, slowapi to api/requirements.txt
- [ ] T002 Add R2 configuration settings to api/app/config.py (r2_access_key_id, r2_secret_access_key, r2_bucket_name, r2_endpoint_url, r2_region)
- [ ] T003 Add R2 credentials and settings to api/.env (R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME, R2_ENDPOINT_URL)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 [P] Implement R2StorageBackend in api/app/upload/utils.py (extend StorageBackend ABC with boto3 S3 client, R2 endpoint, bucket operations)
- [ ] T005 [P] Add python-magic content validation function to api/app/upload/utils.py (validate_pdf_content using magic.from_buffer, return MIME type)
- [ ] T006 [P] Add generate_presigned_upload_url function to api/app/upload/utils.py (boto3 generate_presigned_url with put_object, 900s expiry)
- [ ] T007 [P] Add validation_status column to File model in api/app/models/file.py (String(20), default "pending", values: pending/validated/rejected)
- [ ] T008 [P] Add last_activity column to UploadSession model in api/app/models/upload_session.py (DateTime(tz), default datetime.now(timezone.utc))
- [ ] T009 Create alembic migration 004_add_r2_fields.py adding validation_status to files, last_activity to upload_sessions
- [ ] T010 [P] Add slowapi rate limiter setup to api/app/main.py (Limiter with key function extracting current_user.id; 10/minute default; include CORSMiddleware order)
- [ ] T011 [P] Add new Pydantic schemas to api/app/upload/schemas.py (PresignedUrlRequest, PresignedUrlResponse, UploadCompleteRequest, UploadCompleteResponse)

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel

---

## Phase 3: User Story 1 — Upload Exam Files Securely (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can upload PDF files with server-side content validation, rate limiting, and free tier enforcement. Uploads go through R2 with presigned URLs.

**Independent Test**: A user authenticates, requests a presigned URL, uploads a valid PDF directly to R2, calls complete, and sees the file in their list with validation_status="validated".

### Implementation for User Story 1

- [ ] T012 [US1] Add POST /upload/presign-url endpoint to api/app/upload/router.py (check FR-002 rate limit, FR-003 file limit, FR-004 analysis quota, auto-create UploadSession, generate presigned URL via utils, return PresignedUrlResponse)
- [ ] T013 [US1] Add POST /upload/{file_id}/complete endpoint to api/app/upload/router.py (receive upload completion notification, enqueue content validation RQ job, return UploadCompleteResponse)
- [ ] T014 [US1] Create post-upload validation RQ job module in api/app/upload/validation.py (download file from R2, run python-magic validation, update File status to "validated" or "rejected", log errors to Job table per Constitution V)
- [ ] T015 [US1] Add rate limit decorator @limiter.limit("10/minute") to POST /upload/presign-url and POST /upload/{file_id}/complete in api/app/upload/router.py (via slowapi Limiter dependency)
- [ ] T016 [US1] Add free tier enforcement checks to POST /upload/presign-url in api/app/upload/router.py (FR-003: check user.files_uploaded < 20; FR-004: check user.analyses_used_this_month < 1; return structured error responses per Constitution Quality section)
- [ ] T017 [US1] Update GET /upload/files in api/app/upload/router.py to include validation_status and session_id in FileListItem response
- [ ] T018 [US1] Update GET /upload/limits in api/app/upload/router.py to include analyses_used and analyses_limit in UsageLimitResponse

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. A user can upload a PDF through the full presigned URL flow.

---

## Phase 4: User Story 2 — Upload Large Files Reliably (Priority: P2)

**Goal**: Users can upload large files directly from their browser to R2 without the file data passing through the application server, with proper error handling for expired URLs and network failures.

**Independent Test**: A user uploads a 40MB PDF from the browser, sees progress, and the file appears in their list. Trying to use an expired presigned URL shows a clear error.

### Implementation for User Story 2

- [ ] T019 [US2] Modify upload client in web/src/lib/upload.ts to use presigned URL flow (call POST /upload/presign-url, upload directly to R2 via PUT, call POST /upload/{file_id}/complete)
- [ ] T020 [US2] Update upload page in web/src/app/upload/page.tsx to use the new presigned URL flow instead of the old server-proxy upload
- [ ] T021 [US2] Add frontend error handling for expired presigned URLs in web/src/lib/upload.ts (detect 403 from R2, prompt user to re-request presigned URL)
- [ ] T022 [US2] Add file size validation in web/src/lib/upload.ts (reject files > 50MB on client side before calling presign-url)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Full end-to-end upload flow from browser to R2.

---

## Phase 5: User Story 3 — Track Upload Sessions (Priority: P3)

**Goal**: Upload sessions are automatically created and tracked, with inactivity-based auto-closure after 30 minutes. Users can see session grouping in their file list.

**Independent Test**: A user uploads three files and all share the same session ID. After 30 minutes of inactivity, a new upload creates a new session.

### Implementation for User Story 3

- [ ] T023 [US3] Implement auto-session creation logic in POST /upload/presign-url endpoint in api/app/upload/router.py (query for open session within 30 min inactivity; if none found, create new UploadSession; update last_activity on each upload)
- [ ] T024 [US3] Update GET /upload/session/{session_id} endpoint in api/app/upload/router.py to return auto-closed session status when inactivity exceeds 30 minutes
- [ ] T025 [US3] Add session_id field to GET /upload/files response in api/app/upload/router.py (already done in T017 — verify cross-talk)
- [ ] T026 [US3] Add last_activity update on each call to POST /upload/presign-url in api/app/upload/router.py (update session.last_activity = now on every presigned URL issuance)

**Checkpoint**: All user stories should now be independently functional. Full upload lifecycle with session tracking.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verification, cleanup, and documentation

- [ ] T027 Run full quickstart.md validation suite (9 scenarios from specs/004-r2-upload-storage/quickstart.md)
- [ ] T028 Update AGENTS.md Session Context with 004 feature completion status
- [ ] T029 Clean up deprecated LocalStorageBackend code in api/app/upload/utils.py (keep the abstract StorageBackend class, remove LocalStorageBackend implementation if no longer referenced)
- [ ] T030 Remove old server-proxy upload endpoint POST /upload/{session_id}/files from api/app/upload/router.py if superseded by presigned URL flow (deprecate gracefully — log warning but keep for backward compat during transition)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - US1 (Phase 3) must be complete before US2 (Phase 4) — frontend depends on backend endpoints
  - US3 (Phase 5) has minor dependencies on US1 (session creation in presign-url) but can largely proceed in parallel
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 (Phase 3) — needs presign-url and complete endpoints
- **User Story 3 (P3)**: Depends on US1 (Phase 3) — extends session creation logic in presign-url endpoint

### Recommended Execution Order

Foundation → US1 → US2 → US3 → Polish

### Parallel Opportunities

- All Setup tasks T001-T003 can run in parallel (different files)
- Foundational tasks T004-T011 marked [P] can run in parallel (different files, no dependencies)
- Within US1: T012-T018 must be sequential (router depends on schemas, validation depends on utils)
- Within US2: T019-T022 are sequential (client lib → page → error handling → validation)
- Within US3: T023-T026 are sequential (auto-creation → endpoint update → field update → activity tracking)
- Different phases cannot run in parallel (phase dependencies)

---

## Parallel Example: User Story 1

```bash
# Launch all backend model/config tasks in parallel (Phase 2):
Task: "Implement R2StorageBackend in api/app/upload/utils.py"
Task: "Add python-magic validation in api/app/upload/utils.py"
Task: "Add generate_presigned_upload_url in api/app/upload/utils.py"
Task: "Add validation_status to File model in api/app/models/file.py"
Task: "Add last_activity to UploadSession model in api/app/models/upload_session.py"
Task: "Add slowapi rate limiter to api/app/main.py"
Task: "Add new Pydantic schemas to api/app/upload/schemas.py"

# Once foundational is done, US1 tasks run sequentially:
Task: "Add POST /upload/presign-url endpoint"
Task: "Add POST /upload/{file_id}/complete endpoint"
Task: "Create post-upload validation RQ job in api/app/upload/validation.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T011) — CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T012-T018)
4. **STOP and VALIDATE**: Test US1 independently — upload a PDF via presigned URL flow
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → R2 storage, rate limiting, models ready
2. Add US1 (T012-T018) → Backend upload flow works via API → **MVP**
3. Add US2 (T019-T022) → Frontend browser upload works end-to-end
4. Add US3 (T023-T026) → Session tracking with auto-creation and timeout
5. Add Polish (T027-T030) → Cleanup and validation

### Validation per Quickstart

After each phase, run the relevant quickstart.md scenarios:
- After US1: Scenarios 1-8 (presigned URL, direct upload, complete, rate limit, file limit, analysis quota, unauthenticated, expiry)
- After US2: Re-run scenarios 1-3 from browser (full frontend flow)
- After US3: Scenario 9 (file list with validation_status and session_id)

---

## Notes

- [P] tasks = different files, no dependencies — truly parallelizable
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- The existing 003-file-upload-ui code is the starting point — extend, don't replace
