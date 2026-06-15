---

description: "Task list for Project Foundation feature"

---

# Tasks: Project Foundation

**Input**: Design documents from `specs/001-project-foundation/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL — not requested in this specification. None generated.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `api/` (backend), `web/` (frontend)
- Paths shown reflect the project structure from plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create repository root structure with `api/` and `web/` directories
- [ ] T002 [P] Create docker-compose.yml for PostgreSQL (port 5432, db=examdna, user=postgres, password=devpassword) and Redis (port 6379) at docker-compose.yml
- [ ] T003 [P] Create root .env.example with DATABASE_URL and REDIS_URL at .env.example
- [ ] T004 Initialize Next.js App Router project with TypeScript and Tailwind CSS in web/
- [ ] T005 Set up Python virtual environment and install FastAPI, SQLAlchemy, Alembic, psycopg2, redis-py, uvicorn, pydantic-settings in api/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 [P] Create FastAPI application factory with lifespan and CORS config in api/app/main.py
- [ ] T007 [P] Create Pydantic settings model loading from env vars in api/app/config.py
- [ ] T008 [P] Configure SQLAlchemy engine, session factory, and Base declarative model in api/app/database.py
- [ ] T009 Set up Alembic with env.py (importing Base from database.py), alembic.ini, and script.py.mako in api/
- [ ] T010 [P] Create User SQLAlchemy model (id, email, plan, analyses_used_this_month, is_admin, timestamps) in api/app/models/user.py
- [ ] T011 [P] Create UploadSession SQLAlchemy model (id, user_id FK, status, timestamps) in api/app/models/upload_session.py
- [ ] T012 [P] Create File SQLAlchemy model (id, upload_session_id FK, filename, storage_key, file_size, created_at) in api/app/models/file.py
- [ ] T013 Create models package __init__ exporting all models in api/app/models/__init__.py
- [ ] T014 Generate initial Alembic migration creating users, upload_sessions, and files tables in api/alembic/versions/

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Developer scaffolds new project (Priority: P1) 🎯 MVP

**Goal**: A developer can clone the repo, start Docker services, run migrations, and see both frontend and backend running.

**Independent Test**: Follow setup steps in README → frontend at localhost:3000, backend at localhost:8000/health returns `{"success": true, "data": {"status": "ok"}}`.

### Implementation for User Story 1

- [ ] T015 [P] [US1] Implement GET /health endpoint returning envelope format in api/app/main.py
- [ ] T016 [P] [US1] Create Next.js welcome page with basic Tailwind-styled content at web/src/app/page.tsx
- [ ] T017 [P] [US1] Create Next.js root layout with metadata at web/src/app/layout.tsx
- [ ] T018 [P] [US1] Create Tailwind CSS entry point with @tailwind directives at web/src/app/globals.css
- [ ] T019 [US1] Write README.md with prerequisites and step-by-step setup instructions at README.md

**Checkpoint**: User Story 1 fully functional — developer can run the full stack locally.

---

## Phase 4: User Story 2 - Developer verifies database schema (Priority: P2)

**Goal**: A developer can confirm that Alembic migrations produce the correct schema for all three models.

**Independent Test**: Run `alembic upgrade head` then downgrade; inspect Postgres tables exist with correct columns.

### Implementation for User Story 2

- [ ] T020 [P] [US2] Create backend requirements.txt at api/requirements.txt
- [ ] T021 [P] [US2] Create backend Dockerfile at api/Dockerfile
- [ ] T022 [P] [US2] Create frontend Dockerfile at web/Dockerfile
- [ ] T023 [P] [US2] Create Next.js config at web/next.config.ts
- [ ] T024 [P] [US2] Create TypeScript config at web/tsconfig.json
- [ ] T025 [P] [US2] Create Tailwind config at web/tailwind.config.ts
- [ ] T026 [US2] Run `alembic upgrade head` and `alembic downgrade -1` to verify round-trip migration

**Checkpoint**: All user stories independently functional.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final touches affecting the whole foundation

- [ ] T027 Create .gitignore at repo root excluding node_modules/, __pycache__/, .venv/, .env, .next/
- [ ] T028 [P] Add Python type stubs and mypy config for backend in api/pyproject.toml
- [ ] T029 [P] Add ESLint config for frontend in web/eslint.config.mjs
- [ ] T030 Run quickstart.md validation to verify end-to-end setup works

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Phase 5)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational — No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational — Independent of US1

### Within Each User Story

- Models before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel
- Once Foundational completes, US1 and US2 can start in parallel
- Models within Foundational marked [P] can run in parallel
- Implementation tasks within each user story marked [P] can run in parallel

---

## Parallel Examples

### Foundational Phase

```bash
# Models can be created in parallel:
Task: "T010 [P] Create User model in api/app/models/user.py"
Task: "T011 [P] Create UploadSession model in api/app/models/upload_session.py"
Task: "T012 [P] Create File model in api/app/models/file.py"

# Config files can be created in parallel:
Task: "T006 [P] Create app factory in api/app/main.py"
Task: "T007 [P] Create Pydantic settings in api/app/config.py"
Task: "T008 [P] Configure SQLAlchemy engine in api/app/database.py"
```

### User Story 1

```bash
# Backend and frontend can be done in parallel:
Task: "T015 [P] [US1] Implement health endpoint in api/app/main.py"
Task: "T016 [P] [US1] Create welcome page in web/src/app/page.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run quickstart steps, verify health endpoint
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup together
2. Split Foundational tasks: Dev A (config/models), Dev B (migrations)
3. Once Foundational is done:
   - Dev A: User Story 1 (backend health endpoint)
   - Dev B: User Story 1 (frontend welcome page) + User Story 2 (configs/Dockerfiles)
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
