# Feature Specification: Project Foundation

**Feature Branch**: `001-project-foundation`

**Created**: 2026-06-15

**Status**: Draft

**Input**: User description: "Feature: Project foundation. Set up a Next.js TypeScript frontend and a Python FastAPI backend in the same repo (web/ and api/ folders). The backend connects to Postgres (via SQLAlchemy + Alembic) and Redis, both running in Docker for local development. Define initial database models: User (with plan, analyses_used_this_month, is_admin fields), UploadSession, and File. No business logic yet — just the scaffold and schema."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer scaffolds new project (Priority: P1)

A developer clones the repo, runs a single setup command, and has both
frontend and backend running locally with database tables created.

**Why this priority**: This is the foundational developer experience —
everything else depends on a working local environment.

**Independent Test**: A developer can run the project setup steps and
verify that the frontend dev server starts, the backend API responds,
and database tables exist.

**Acceptance Scenarios**:

1. **Given** a fresh clone of the repository, **When** the developer
   follows the setup instructions (start Docker services, run
   migrations, start dev servers), **Then** the backend API responds
   on its configured port with a health-check endpoint returning 200.
2. **Given** the backend is running, **When** the developer inspects
   the database via `psql` or an admin tool, **Then** the `users`,
   `upload_sessions`, and `files` tables exist with the expected
   columns.

---

### User Story 2 - Developer verifies database schema (Priority: P2)

A developer can confirm that Alembic migrations produce the correct
schema for the three initial models.

**Why this priority**: Correct schema is a prerequisite for all future
data-dependent work.

**Independent Test**: Running `alembic upgrade head` then inspecting
the database shows all three tables with correct columns.

**Acceptance Scenarios**:

1. **Given** a PostgreSQL instance is running, **When** the developer
   runs `alembic upgrade head`, **Then** the migration completes
   without error.
2. **Given** migrations have been applied, **When** the developer runs
   `alembic downgrade -1`, **Then** the most recent migration is
   rolled back cleanly.

### Edge Cases

- What happens when Docker is not installed? Setup instructions should
  document Docker as a prerequisite.
- What if port 5432 or 6379 is already in use? Docker Compose should
  expose configurable ports via environment variables.
- What if a migration fails mid-way? Alembic transactional DDL should
  prevent partial application (Postgres enforces this).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Repository MUST contain a `web/` directory with a
  Next.js (App Router) TypeScript project initialized with Tailwind
  CSS.
- **FR-002**: Repository MUST contain an `api/` directory with a
  Python FastAPI project including SQLAlchemy models and Alembic
  migration setup.
- **FR-003**: Repository MUST include a `docker-compose.yml` at the
  root that starts PostgreSQL and Redis containers for local
  development.
- **FR-004**: Backend MUST connect to PostgreSQL via SQLAlchemy, with
  connection string configurable via environment variable.
- **FR-005**: Backend MUST connect to Redis via `redis-py`, with
  connection details configurable via environment variable.
- **FR-006**: Alembic MUST be configured with an initial migration
  that creates the `users` table with columns: `id` (UUID primary
  key), `email` (unique, not null), `plan` (string, default 'free'),
  `analyses_used_this_month` (integer, default 0), `is_admin`
  (boolean, default false), plus standard timestamps.
- **FR-007**: Alembic MUST create the `upload_sessions` table with
  columns: `id` (UUID primary key), `user_id` (foreign key to users),
  `status` (string), `created_at`, `updated_at`.
- **FR-008**: Alembic MUST create the `files` table with columns:
  `id` (UUID primary key), `upload_session_id` (foreign key to
  upload_sessions), `filename` (string), `storage_key` (string),
  `file_size` (integer), `created_at`.
- **FR-009**: Backend MUST expose a health-check endpoint at
  `GET /health` that returns a 200 response with the standard
  envelope format: `{"success": true, "data": {"status": "ok"}}`.
- **FR-010**: Frontend MUST display a basic welcome/home page on
  `GET /` without errors.

### Key Entities *(include if feature involves data)*

- **User**: Represents a registered user. Fields: id (UUID), email,
  plan (free/pro), analyses_used_this_month (counter), is_admin
  (boolean), timestamps.
- **UploadSession**: Groups file uploads into a single session.
  Fields: id (UUID), user_id (FK to User), status (pending/processing/
  completed/failed), timestamps.
- **File**: An uploaded file within a session. Fields: id (UUID),
  upload_session_id (FK to UploadSession), filename, storage_key,
  file_size (bytes), created_at.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can go from `git clone` to running
  frontend + backend in under 15 minutes by following the README.
- **SC-002**: The `docker-compose up` command starts both Postgres
  and Redis without errors.
- **SC-003**: A developer can verify the database contains exactly
  three tables (`users`, `upload_sessions`, `files`) with all
  specified columns after running the setup commands.
- **SC-004**: The frontend dev server starts and renders a page
  without console errors.

## Clarifications

### Session 2026-06-15

- Q: Should the scaffold include logging infrastructure setup?
  → A: Defer logging to a later task — the scaffold is purely structural
- Q: What response format should the health check endpoint use?
  → A: Use the standard envelope format `{"success": true, "data": {"status": "ok"}}`

## Assumptions

- Developers have Docker Desktop (or compatible Docker runtime)
  installed on their machine.
- The project will use Python 3.11+ and Node.js 18+.
- PostgreSQL 16 and Redis 7 will be used in development.
- Authentication is out of scope for this foundation phase — the
  User model is defined but no auth endpoints are implemented yet.
- The default `plan` value is `"free"` for all new users.
- No business logic, API routes (beyond health-check), or frontend
  pages (beyond a welcome page) are required at this stage.
