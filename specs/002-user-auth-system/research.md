# Research: User Authentication System

**Date**: 2026-06-15 | **Feature**: [spec.md](./spec.md)

## Overview

Research decisions for the auth system based on the project constitution, feature spec, and industry best practices for FastAPI + Next.js authentication.

## Auth Library Decision

**Decision**: Use `fastapi-users` with SQLAlchemy adapter + `httpx-oauth` for Google OAuth.

**Rationale**: `fastapi-users` provides ready-made JWT flow, password hashing, OAuth integration, and Pydantic schemas — eliminating boilerplate while staying within the FastAPI ecosystem. It natively supports SQLAlchemy and Alembic migrations.

**Alternatives considered**:
- **Custom auth from scratch**: More flexible but adds significant boilerplate (password hashing, JWT creation/validation, session management, OAuth callback handling). Rejected to avoid re-inventing the wheel.
- **Authlib**: Powerful but more complex setup for basic email/password + Google OAuth. Better suited for multi-provider enterprise auth.
- **NextAuth.js**: Frontend-only solution that doesn't integrate with FastAPI backend. Would require a separate session bridge layer.

## Session Strategy

**Decision**: Database-backed JWT stored in httpOnly secure cookie. 7-day token expiry with no refresh token (simplified for v1).

**Rationale**: httpOnly cookies prevent XSS-based token theft. Database-backed sessions allow server-side invalidation (sign-out from any device). 7-day expiry matches the spec requirement (SC-003) without refresh token complexity.

**Alternatives considered**:
- **Stateless JWTs (no DB lookup)**: Faster but cannot invalidate individual sessions server-side. If a token is leaked, it remains valid until expiry.
- **Refresh token pattern**: Access token (short-lived, 15min) + refresh token (long-lived, 7 days). Adds complexity for marginal benefit at this scale (<1000 users). Deferred for future scale.
- **Redis-backed sessions**: Faster DB lookups but introduces Redis as a runtime dependency for auth. PostgreSQL sessions are sufficient at expected scale.

## Password Hashing

**Decision**: bcrypt via `passlib`.

**Rationale**: Industry standard for password hashing. `fastapi-users` uses `passlib` with bcrypt by default. Automatically handles salting and cost factor.

**Alternatives considered**: argon2 (more resistant to GPU attacks but slower, higher overhead for server), scrypt (memory-hard but less ecosystem support in Python).

## Google OAuth Flow

**Decision**: Authorization code flow (server-side). Backend handles the OAuth callback, exchanges the code for tokens, creates/links the user account, and issues a session cookie.

**Rationale**: The authorization code flow is the most secure OAuth 2.0 flow for web apps. The backend stores the client secret (never exposed to the browser). `httpx-oauth` handles the HTTP exchanges.

**Flow**:
1. User clicks "Sign in with Google" → redirected to Google consent screen.
2. Google redirects to backend callback URL (`/auth/google/callback`).
3. Backend exchanges code for tokens, looks up or creates user by email.
4. Backend issues JWT session cookie and redirects to frontend dashboard.

## CORS Configuration

**Decision**: Allow `http://localhost:3000` (dev) and production frontend origin. Credentials: true (for cookies). Methods: GET, POST, OPTIONS.

**Rationale**: The frontend runs on a different port during development. Cookies require `credentials: true` and specific `Access-Control-Allow-Origin` (cannot use `*`).

## Frontend Auth Architecture

**Decision**: Server-side cookie-based auth with a React context for session state.

**Rationale**: httpOnly cookies are sent automatically with `credentials: 'include'` fetch requests. No need to manually manage token storage in localStorage. The auth context provides a simple `useAuth()` hook that exposes the current user and login/logout actions.

**Protected route strategy**: A `ProtectedLayout` wrapper component checks for a valid session on mount. If no session cookie exists, the user is redirected to `/login`. If the session is invalid/expired, the API returns 401 and the frontend clears the context and redirects.

## Summary of Key Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Auth framework | fastapi-users[sqlalchemy] | Ready-made JWT + OAuth, SQLAlchemy native |
| OAuth provider | httpx-oauth | fastapi-users integration, Google support |
| Session storage | PostgreSQL (DB-backed JWT) | Server-side invalidation, no extra Redis dependency |
| Token expiry | 7 days, no refresh token | Simplified v1, matches spec SC-003 |
| Cookie type | httpOnly, Secure, SameSite=Lax | XSS protection, CSRF mitigation |
| Password hash | bcrypt via passlib | Industry standard, fastapi-users default |
| Frontend auth | React context + httpOnly cookies | Simple, secure, no token management in JS |
| CORS | Specific origin + credentials: true | Required for cross-origin cookie auth |
