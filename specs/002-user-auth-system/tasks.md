---
description: "Task list for user authentication system implementation"
---

# Tasks: User Authentication System

**Input**: Design documents from `specs/002-user-auth-system/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Not requested in feature spec — no test tasks generated.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `api/` directory
- **Frontend**: `web/` directory
- Paths shown below follow the monorepo structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install new dependencies and configure environment variables for auth

- [x] T001 Add auth dependencies to `api/requirements.txt` (fastapi-users[sqlalchemy], httpx-oauth, python-jose[cryptography], passlib[bcrypt])
- [x] T002 Add auth environment variables to `api/.env.example` (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, JWT_SECRET, JWT_EXPIRY)
- [x] T003 Add auth settings to `api/app/config.py` (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, JWT_SECRET, JWT_EXPIRY fields)
- [x] T004 [P] Run `pip install -r api/requirements.txt` to install new dependencies

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Backend auth infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create `api/app/auth/` package with `api/app/auth/__init__.py`
- [x] T006 [P] Update `api/app/models/user.py` — add `password_hash` (nullable String(255)), `is_active` (Boolean, default True)
- [x] T007 [P] Create `api/app/auth/utils.py` — JWT creation and validation helpers with python-jose
- [x] T008 [P] Create `api/app/auth/schemas.py` — Pydantic models for auth requests/responses (email+password, user response, error envelope)
- [x] T009 [P] Create `api/app/auth/dependencies.py` — `get_current_user` dependency that validates JWT from httpOnly cookie
- [x] T010 Create Alembic migration `api/alembic/versions/002_add_auth_fields.py` — add password_hash, is_active to users; create oauth_identities table
- [x] T011 Update `api/app/models/__init__.py` — export OAuthIdentity model

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel

---

## Phase 3: User Story 1 — Sign Up with Email & Password (Priority: P1) 🎯 MVP

**Goal**: A new visitor can create an account with email + password and be automatically logged in

**Independent Test**: Send POST to `/auth/register` with valid email + password → receive 201 + user object + session cookie

### Implementation for User Story 1

- [x] T012 [P] [US1] Create `api/app/auth/router.py` — include POST /auth/register endpoint (validate input, hash password, create user, issue JWT cookie, return user)
- [x] T013 [P] [US1] Create `web/src/app/register/page.tsx` — signup form with email + password fields, submit to POST /auth/register, redirect to / on success
- [x] T014 [P] [US1] Create `web/src/lib/auth.tsx` — auth context provider, user state, login/logout helpers with `credentials: 'include'`
- [x] T015 [P] [US1] Create `web/src/components/ProtectedLayout.tsx` — wrapper that checks auth state, redirects to /login if not authenticated
- [x] T016 [US1] Register auth router in `api/app/main.py` — mount `/auth` prefix, configure CORS for frontend origin

**Checkpoint**: At this point, User Story 1 should be fully functional — user can sign up via browser or curl, get a session cookie, and see the dashboard

---

## Phase 4: User Story 2 — Sign In with Email & Password (Priority: P1)

**Goal**: A returning user can sign in with their credentials and access protected pages

**Independent Test**: Sign up, sign out (clear cookie), POST /auth/jwt/login with same credentials → receive 200 + user object + new session cookie

### Implementation for User Story 2

- [x] T017 [P] [US2] Add POST /auth/jwt/login to `api/app/auth/router.py` — verify email+password, issue JWT cookie, return user
- [x] T018 [P] [US2] Create `web/src/app/login/page.tsx` — login form with email + password fields, submit to POST /auth/jwt/login, redirect to / on success

**Checkpoint**: User Story 2 complete — user can sign up, sign out, sign back in, and access protected pages

---

## Phase 5: User Story 3 — Sign In with Google (Priority: P1)

**Goal**: A visitor can sign up or sign in using their Google account

**Independent Test**: Click "Sign in with Google" → complete Google auth → redirected to dashboard as logged-in user

### Implementation for User Story 3

- [x] T019 [P] [US3] Add GET /auth/google to `api/app/auth/router.py` — redirect to Google OAuth consent screen
- [ ] T020 [P] [US3] Add GET /auth/google/callback to `api/app/auth/router.py` — exchange code for tokens, find or create user by email, link OAuthIdentity, issue JWT cookie, redirect to frontend
- [ ] T021 [P] [US3] Create `api/app/models/oauth_identity.py` — OAuthIdentity model (id, user_id FK, provider, provider_user_id, created_at)
- [ ] T022 [US3] Add "Sign in with Google" button to `web/src/app/login/page.tsx` — link to GET /auth/google

**Checkpoint**: User Story 3 complete — Google OAuth works end-to-end alongside email/password login

---

## Phase 6: User Story 4 — Session Persistence + User Story 6 — Sign Out (Priority: P2)

**Goal**: Authenticated session survives page reloads and browser restarts. User can explicitly sign out.

**Independent Test**: Login, refresh browser → still authenticated. Click sign out → redirected to login. Accessing protected page → redirected to login.

### Implementation for User Story 4 & 6

- [ ] T023 [P] [US4] Add POST /auth/logout to `api/app/auth/router.py` — clear JWT cookie with immediate expiry
- [ ] T024 [P] [US4] Implement auth context provider in `web/src/lib/auth.tsx` — React context that calls GET /auth/me on mount to check session, provides `user`, `loading`, `login()`, `logout()` to children
- [ ] T025 [P] [US4] Refactor `web/src/app/layout.tsx` — wrap with AuthProvider, add header with user menu (email + sign out button)
- [ ] T026 [US4] Apply ProtectedLayout to `/profile` page route — redirect to /login if no valid session
- [ ] T027 [US4] Update root `web/src/app/page.tsx` — show dashboard view for authenticated users, redirect to /login for unauthenticated

**Checkpoint**: Session flows complete — login persists across reloads, sign out works, unauthenticated access is blocked

---

## Phase 7: User Story 5 — View Profile & Plan Badge (Priority: P2)

**Goal**: Authenticated user can see their email and plan badge on a profile page

**Independent Test**: Login, navigate to /profile → see email and "Free" badge

### Implementation for User Story 5

- [ ] T028 [P] [US5] Add GET /auth/me to `api/app/auth/router.py` — return current user profile (id, email, plan, analyses_used_this_month, is_admin)
- [ ] T029 [P] [US5] Create `web/src/app/profile/page.tsx` — display user email, plan badge, account creation date, wrapped in ProtectedLayout

**Checkpoint**: User Story 5 complete — profile page shows user info with plan badge

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Finalize auth system — CORS hardening, env doc updates, validation

- [ ] T030 [P] Configure CORS in `api/app/main.py` — allow frontend origin (`http://localhost:3000`) with credentials, restrict methods to GET/POST/OPTIONS
- [ ] T031 [P] Update `api/.env.example` with all auth env vars and descriptive comments
- [ ] T032 [P] Update `README.md` — add auth setup instructions (Google OAuth credentials, JWT secret generation)
- [ ] T033 Run quickstart validation scenarios from `specs/002-user-auth-system/quickstart.md` — confirm all flows pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **US1 Sign Up (Phase 3)**: Depends on Foundational completion — 🎯 MVP scope
- **US2 Sign In (Phase 4)**: Depends on Foundational completion (US2 login endpoint is separate from US1 register, can be done in parallel if staffed)
- **US3 Google OAuth (Phase 5)**: Depends on Foundational + OAuthIdentity model creation
- **US4+US6 Session & Sign Out (Phase 6)**: Depends on Foundational + US2 for login page, US1 for register page
- **US5 Profile (Phase 7)**: Depends on Phase 6 (needs ProtectedLayout and auth context)
- **Polish (Phase 8)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories
- **US2 (P1)**: Can start after Foundational (Phase 2) — Independent from US1 (login is separate from register)
- **US3 (P1)**: Can start after Foundational (Phase 2) + OAuthIdentity model — Independent from US1/US2
- **US4+US6 (P2)**: Can start after Foundational (Phase 2) — Needs login/register pages for full testing
- **US5 (P2)**: Can start after Foundational (Phase 2) — Needs ProtectedLayout and auth context

### Within Each User Story

- Implementation tasks can proceed in parallel where marked [P]
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel
- Once Foundational phase completes: US1, US2, and US3 can start in parallel
- Within each user story, frontend and backend tasks can run in parallel
- Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tasks for User Story 1 together:
Task: "Create POST /auth/register endpoint in api/app/auth/router.py"
Task: "Create register page in web/src/app/register/page.tsx"
Task: "Create auth helpers in web/src/lib/auth.ts"
Task: "Create ProtectedLayout in web/src/components/ProtectedLayout.tsx"
Task: "Register auth router in api/app/main.py"
```

---

## Parallel Example: User Story 3

```bash
# Launch all tasks for User Story 3 together:
Task: "Add GET /auth/google redirect endpoint in api/app/auth/router.py"
Task: "Add GET /auth/google/callback handler in api/app/auth/router.py"
Task: "Create OAuthIdentity model in api/app/models/oauth_identity.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test signup end-to-end (backend via curl, frontend via browser)
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Auth infrastructure ready
2. Add US1 (Sign Up) → Test independently → 🎯 MVP!
3. Add US2 (Sign In) → Test independently → Users can sign in
4. Add US3 (Google OAuth) → Test independently → Two auth methods
5. Add US4+US6 (Session + Sign Out) → Session management complete
6. Add US5 (Profile Page) → User self-service complete
7. Polish → Production-ready

### Single Developer Strategy

1. Complete Phase 1: Setup
2. Complete Phase 1 → Phase 2 sequentially (blocks everything)
3. Complete US1 → US2 → US3 sequentially (P1 stories in priority order)
4. Complete US4+US6 → US5 (P2 stories)
5. Polish last

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Test via curl for backend endpoints and browser for full frontend flows
- No test framework tasks — feature spec did not request tests
