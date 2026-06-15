# API Contracts: User Authentication System

**Date**: 2026-06-15 | **Feature**: [spec.md](../spec.md) | **Data Model**: [data-model.md](../data-model.md)

## Envelope Format

All responses follow the standard envelope:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

On error:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description"
  }
}
```

## Endpoints

### POST /auth/register

Create a new account with email and password.

**Request body**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "plan": "free",
    "is_admin": false,
    "created_at": "2026-06-15T00:00:00Z"
  },
  "error": null
}
```

**Errors**:
- `409` — Email already registered
- `422` — Validation error (invalid email format, password < 8 chars)

**Cookie set**: `access_token` (httpOnly, 7-day expiry)

---

### POST /auth/jwt/login

Sign in with email and password.

**Request body**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "plan": "free",
    "is_admin": false
  },
  "error": null
}
```

**Errors**:
- `401` — Invalid email or password (unified message, no field-specific hints)

**Cookie set**: `access_token` (httpOnly, 7-day expiry)

---

### POST /auth/logout

Sign out the current user.

**Request**: No body. Cookie sent automatically.

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "message": "Logged out successfully"
  },
  "error": null
}
```

**Cookie cleared**: `access_token` set to empty with immediate expiry.

---

### GET /auth/google

Initiate Google OAuth flow. Redirects to Google consent screen.

**Query parameters**: None.

**Response**: HTTP 302 redirect to `https://accounts.google.com/o/oauth2/v2/auth?...`

---

### GET /auth/google/callback

Google OAuth callback URL. Handles the authorization code exchange.

**Query parameters** (`code`, `state`, `error` — provided by Google).

**Response**: HTTP 302 redirect to `http://localhost:3000/` (dev) or production frontend URL.

**Cookie set**: `access_token` (httpOnly, 7-day expiry) on success.

**Errors**: Redirect to frontend with `?error=access_denied` query param if user denies or flow fails.

---

### GET /auth/me

Get the currently authenticated user's profile.

**Request**: Cookie sent automatically.

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "plan": "free",
    "analyses_used_this_month": 0,
    "is_admin": false,
    "created_at": "2026-06-15T00:00:00Z"
  },
  "error": null
}
```

**Errors**:
- `401` — Not authenticated (missing/expired/invalid token)

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTH_INVALID_CREDENTIALS` | 401 | Wrong email or password |
| `AUTH_TOKEN_EXPIRED` | 401 | Session token has expired |
| `AUTH_NOT_AUTHENTICATED` | 401 | No valid session |
| `AUTH_EMAIL_EXISTS` | 409 | Email already registered |
| `AUTH_GOOGLE_FAILED` | 502 | Google OAuth provider error |
| `VALIDATION_ERROR` | 422 | Request body validation failed |

## CORS Configuration

| Setting | Value |
|---------|-------|
| `allow_origins` | `["http://localhost:3000", "<production-url>"]` |
| `allow_credentials` | `true` |
| `allow_methods` | `["GET", "POST", "OPTIONS"]` |
| `allow_headers` | `["*"]` |
