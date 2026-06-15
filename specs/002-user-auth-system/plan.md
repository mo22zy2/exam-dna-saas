# Implementation Plan: User Authentication System

**Branch**: `002-user-auth-system` | **Date**: 2026-06-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/002-user-auth-system/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add user authentication to the Exam DNA SaaS platform: email/password signup and login, Google OAuth, JWT-based session management in httpOnly cookies, protected frontend routes, and a profile page with plan badge. Backend endpoints handle registration, login, logout, Google OAuth callback, and profile retrieval. The frontend gets login (`/login`), signup (`/register`), and profile (`/profile`) pages with a protected layout that redirects unauthenticated users.

## Technical Context

**Language/Version**: Python 3.12+ (backend), Node.js 20 LTS (frontend), TypeScript 5.x

**Primary Dependencies**:
- Backend: FastAPI, SQLAlchemy 2.x, Alembic, psycopg2, redis-py, uvicorn, pydantic, pydantic-settings, `fastapi-users[sqlalchemy]`, `httpx-oauth`, `python-jose[cryptography]` (JWT), `passlib[bcrypt]` (password hashing)
- Frontend: Next.js 16, React 19, TypeScript, Tailwind CSS v4

**Storage**: PostgreSQL 16 (User, Session, OAuthIdentity tables), Redis 7 (optional session cache/rate limiting)

**Testing**: pytest (backend), vitest + React Testing Library (frontend)

**Target Platform**: Linux server (production), Windows (dev via Docker for Postgres/Redis)

**Project Type**: web-service (`api/`) + web-app (`web/`) in single monorepo

**Performance Goals**: Signup completes in under 30s, login in under 10s (per spec SC-001/SC-002). Token validation < 50ms on backend.

**Constraints**: Per constitution — FastAPI + SQLAlchemy + Alembic (not Prisma), Pydantic validation on all endpoints, envelope response format (`{success, data, error}`). httpOnly cookie for JWT (XSS protection).

**Scale/Scope**: Single-developer project, initial expected user base < 1000. Session store in PostgreSQL (no Redis dependency for auth).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Tech Stack)**: ✅ FastAPI + SQLAlchemy + Alembic backend, Next.js + TypeScript + Tailwind frontend. No Prisma, no Celery, no BullMQ.
- **Principle II (LLM Abstraction)**: ✅ N/A — auth has no LLM calls.
- **Principle III (Input Validation)**: ✅ Pydantic models used for all auth request bodies (register, login, OAuth callback).
- **Principle IV (Server-Side Enforcement)**: ✅ Free-tier limits (analyses_used_this_month) enforced server-side; auth routes check plan status where needed.
- **Principle V (Job Reliability)**: ✅ N/A — no async RQ jobs in auth scope.
- **Development Constraints**: ✅ Changes scoped to auth system only. No unrelated refactoring.
- **Quality & Observability**: ✅ Structured logging on auth events (login, signup, logout, failed attempts). Envelope response format for all auth endpoints.

**Gate verdict**: PASS — all principles satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/002-user-auth-system/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── api.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
api/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app, CORS config
│   ├── config.py                # Settings: DATABASE_URL, REDIS_URL, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, JWT_SECRET, JWT_EXPIRY
│   ├── database.py              # SQLAlchemy engine + session
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── router.py            # /auth/register, /auth/jwt/login, /auth/logout, /auth/google, /auth/me
│   │   ├── schemas.py           # Pydantic models for auth requests/responses
│   │   ├── dependencies.py      # get_current_user dependency
│   │   └── utils.py             # JWT creation/validation, password hashing
│   └── models/
│       ├── __init__.py
│       ├── user.py              # User model (updated: password_hash)
│       ├── upload_session.py
│       └── file.py
├── alembic/
│   └── versions/
│       └── 002_add_auth_fields.py  # Migration: add password_hash, oauth_identity table
├── alembic.ini
├── requirements.txt
└── .env.example

web/
├── src/
│   ├── app/
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx             # Welcome / landing page
│   │   ├── login/
│   │   │   └── page.tsx         # Login page
│   │   ├── register/
│   │   │   └── page.tsx         # Signup page
│   │   ├── profile/
│   │   │   └── page.tsx         # Profile page
│   │   └── globals.css
│   ├── lib/
│   │   └── auth.ts              # Auth helpers: fetch with credentials, session context
│   └── components/
│       └── ProtectedLayout.tsx   # Wrapper that redirects to /login if no session
├── next.config.ts
├── package.json
├── tsconfig.json
└── Dockerfile
```

**Structure Decision**: Monorepo with `api/` (backend) and `web/` (frontend) at repo root. Auth logic in `api/app/auth/` module. Frontend pages in `web/src/app/` (Next.js App Router). Matches the existing scaffold structure from project foundation.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations — all constitution principles satisfied.
