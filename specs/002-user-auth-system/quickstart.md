# Quickstart: User Authentication System

**Date**: 2026-06-15 | **Feature**: [spec.md](./spec.md) | **API**: [contracts/api.md](./contracts/api.md)

## Prerequisites

- Docker Compose running (Postgres on port 5432, Redis on port 6379)
- Backend running at `http://localhost:8000`
- Frontend running at `http://localhost:3000`
- Python venv activated in `api/`

## Setup

### 1. Install dependencies

```powershell
cd api
pip install fastapi-users[sqlalchemy] httpx-oauth python-jose[cryptography] passlib[bcrypt]
```

### 2. Add environment variables

Add to `api/.env`:
```env
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
JWT_SECRET=a-random-secret-at-least-32-chars
JWT_EXPIRY=604800  # 7 days in seconds
```

### 3. Run migration

```powershell
cd api
alembic upgrade head
```

### 4. Restart backend

```powershell
uvicorn app.main:app --reload --port 8000
```

## Validation Scenarios

### Scenario 1: Email/Password Signup

```powershell
curl.exe -X POST http://localhost:8000/auth/register `
  -H "Content-Type: application/json" `
  -d '{"email": "test@example.com", "password": "password123"}'
```

**Expected**: `201 Created` with user object in response body. Cookie `access_token` set.

### Scenario 2: Email/Password Login

```powershell
curl.exe -X POST http://localhost:8000/auth/jwt/login `
  -H "Content-Type: application/json" `
  -d '{"email": "test@example.com", "password": "password123"}' `
  -c cookies.txt
```

**Expected**: `200 OK` with user object. Cookie saved to `cookies.txt`.

### Scenario 3: Get Current User

```powershell
curl.exe http://localhost:8000/auth/me -b cookies.txt
```

**Expected**: `200 OK` with user profile including `plan: "free"` and `is_admin: true` (first user).

### Scenario 4: Invalid Login

```powershell
curl.exe -X POST http://localhost:8000/auth/jwt/login `
  -H "Content-Type: application/json" `
  -d '{"email": "test@example.com", "password": "wrongpassword"}'
```

**Expected**: `401 Unauthorized` with `{"success": false, "error": {"code": "AUTH_INVALID_CREDENTIALS", ...}}`.

### Scenario 5: Duplicate Signup

```powershell
curl.exe -X POST http://localhost:8000/auth/register `
  -H "Content-Type: application/json" `
  -d '{"email": "test@example.com", "password": "password123"}'
```

**Expected**: `409 Conflict` with `{"success": false, "error": {"code": "AUTH_EMAIL_EXISTS", ...}}`.

### Scenario 6: Sign Out

```powershell
curl.exe -X POST http://localhost:8000/auth/logout -b cookies.txt -c cookies.txt
```

**Expected**: `200 OK`. Cookie cleared. Subsequent `GET /auth/me` with same cookie returns `401`.

### Scenario 7: Unauthenticated Access (Frontend)

1. Open `http://localhost:3000/profile` in a private/incognito window.
2. **Expected**: Redirected to `http://localhost:3000/login`.

### Scenario 8: First User is Admin

1. Sign up with a new email.
2. `GET /auth/me`.
3. **Expected**: `is_admin: true`.

### Scenario 9: Second User is Not Admin

1. Sign up with a different email.
2. `GET /auth/me`.
3. **Expected**: `is_admin: false`.

### Scenario 10: Session Persistence

1. Sign up/login.
2. Close browser, reopen.
3. Navigate to `http://localhost:3000/profile`.
4. **Expected**: Still authenticated (no redirect to login).

## Google OAuth (Manual Test)

1. Open `http://localhost:3000/login` in browser.
2. Click "Sign in with Google".
3. Complete Google authorization.
4. **Expected**: Redirected to dashboard, authenticated.
