# Implementation Plan: Project Foundation

**Branch**: `001-project-foundation` | **Date**: 2026-06-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-project-foundation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Set up the monorepo scaffold: `api/` (Python/FastAPI with SQLAlchemy +
Alembic, connected to Postgres + Redis via Docker) and `web/` (Next.js
App Router + TypeScript + Tailwind). Define initial DB models — User,
UploadSession, File — with an initial Alembic migration. No business
logic.

## Technical Context

**Language/Version**: Python 3.12+, Node.js 20 LTS

**Primary Dependencies**:
- Backend: FastAPI, SQLAlchemy 2.x, Alembic, psycopg2, redis-py,
  `uvicorn`, `pydantic`, `python-dotenv`
- Frontend: Next.js 15, React 19, TypeScript, Tailwind CSS v4
- Infra: Docker Compose (PostgreSQL 16, Redis 7)

**Storage**: PostgreSQL 16, Redis 7 (both via Docker)

**Testing**: pytest (backend), vitest (frontend) — deferred to
subsequent feature tasks

**Target Platform**: Linux server (production), macOS/Windows (dev
via Docker)

**Project Type**: web-service (`api/`) + web-app (`web/`) in single
monorepo

**Performance Goals**: N/A — scaffold phase, no business logic

**Constraints**: Per constitution — FastAPI + SQLAlchemy + Alembic
(not Prisma), RQ + Redis (not Celery), Pydantic validation on all
endpoints

**Scale/Scope**: Developer workstation; single monorepo

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1
design.*

- **Principle I (Tech Stack)**: ✅ Fully aligned — FastAPI, SQLAlchemy,
  Alembic, Next.js, Tailwind, RQ + Redis specified
- **Principle II (LLM Abstraction)**: ✅ N/A at scaffold phase — no
  LLM calls
- **Principle III (Input Validation)**: ✅ Health check endpoint uses
  standard envelope format; Pydantic validation deferred to first
  real endpoint
- **Principle IV (Server-Side Enforcement)**: ✅ N/A — no free-tier
  logic yet
- **Principle V (Job Reliability)**: ✅ N/A — no async jobs yet
- **Development Constraints**: ✅ Scoped to scaffold only
- **Quality & Observability**: ⚠ Logging deferred per clarification;
  health check uses envelope format

**Gate verdict**: PASS — violations are justified (scaffold phase,
no business logic). Complexity Tracking not required.

## Project Structure

### Documentation (this feature)

```text
specs/001-project-foundation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # (created by /speckit.tasks)
```

### Source Code (repository root)

```text
# Option 2: Web application (frontend + backend)
api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, health endpoint
│   ├── database.py          # SQLAlchemy engine + session
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── upload_session.py
│   │   └── file.py
│   └── config.py            # Settings from env vars
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial.py
├── alembic.ini
├── requirements.txt
├── Dockerfile
└── .env.example

web/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx         # Welcome page
│   │   └── globals.css
│   └── ...
├── public/
├── next.config.ts
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── Dockerfile

docker-compose.yml
.env.example
README.md
```

**Structure Decision**: Option 2 — Web application with `api/` and
`web/` at repo root. Matches the user's explicit requirement for
separate `api/` and `web/` directories.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

N/A — no violations.
