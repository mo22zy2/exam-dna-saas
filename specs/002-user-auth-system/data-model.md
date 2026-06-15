# Data Model: User Authentication System

**Date**: 2026-06-15 | **Feature**: [spec.md](./spec.md)

## Entities

### User

The existing `User` model gets an additional field. Table: `users`.

| Field | Type | Constraints | Default | Notes |
|-------|------|-------------|---------|-------|
| `id` | UUID (PK) | Auto-generated | `uuid4()` | |
| `email` | String(255) | NOT NULL, UNIQUE, INDEX | — | Canonical email, used for login |
| `password_hash` | String(255) | NULLABLE | `null` | bcrypt hash. Null for Google-only users until they set a password |
| `plan` | String(20) | NOT NULL | `"free"` | `free` or `pro` |
| `analyses_used_this_month` | Integer | NOT NULL | `0` | Reset monthly (logic deferred) |
| `is_admin` | Boolean | NOT NULL | `false` | First user auto-set to `true` |
| `is_active` | Boolean | NOT NULL | `true` | Soft-disable flag |
| `created_at` | DateTime(tz) | NOT NULL | `now()` | |
| `updated_at` | DateTime(tz) | NOT NULL, ON UPDATE | `now()` | |

**Relationships**:
- `User 1 → * OAuthIdentity`: One user can have multiple OAuth provider links.
- `User 1 → * UploadSession`: Existing relationship from foundation.

**Validation rules**:
- Email: valid email format, max 255 chars, unique.
- Password (when set): min 8 chars, hashed with bcrypt before storage.
- Plan: must be one of `free` or `pro` (enum-like validation).
- is_admin: only controllable by existing admin users or auto-set for first user.

### OAuthIdentity

Links a third-party OAuth provider account to a User. Table: `oauth_identities`.

| Field | Type | Constraints | Default | Notes |
|-------|------|-------------|---------|-------|
| `id` | UUID (PK) | Auto-generated | `uuid4()` | |
| `user_id` | UUID (FK → users.id) | NOT NULL, INDEX | — | Cascading delete |
| `provider` | String(50) | NOT NULL | — | e.g. `"google"` |
| `provider_user_id` | String(255) | NOT NULL | — | The user's ID on the provider side |
| `created_at` | DateTime(tz) | NOT NULL | `now()` | |

**Uniqueness**: Composite unique on `(provider, provider_user_id)` — one provider user links to at most one local account.

**Validation rules**:
- `provider` + `provider_user_id` must be unique together.
- A user can have at most one identity per provider (enforced application-side or via unique constraint).

### Session

Backed by JWT stored in httpOnly cookie. No dedicated DB table — sessions are stateless JWTs with the user ID encoded. Stateful session invalidation is achieved by checking user `is_active` flag on each request.

**Token payload**:
```json
{
  "sub": "<user-uuid>",
  "exp": "<expiry-timestamp>",
  "iat": "<issued-at-timestamp>"
}
```

**Cookie**:
- Name: `access_token`
- httpOnly: `true`
- Secure: `true` (production), ignored in dev (HTTP)
- SameSite: `lax`
- Path: `/`
- Max-Age: 604800 (7 days, matches SC-003)

### Key Relationships

```
User (1) ──< (0..*) OAuthIdentity
  │
  └──< (0..*) UploadSession  (existing from foundation)
```

## State Transitions

### User Account States

```
[Unregistered] → signup(email, pw) → [Active]
[Unregistered] → google_oauth(email) → [Active]
[Active] → set_password(pw) → [Active]  (Google-only user sets password)
[Active] → admin_disables() → [Disabled]
[Disabled] → admin_enables() → [Active]
```

### Session States

```
[No Session] → login(email, pw) → [Active Session]  (7-day expiry)
[No Session] → google_oauth() → [Active Session]
[Active Session] → logout() → [No Session]
[Active Session] → expiry() → [No Session]
[Active Session] → user_disabled() → [No Session]  (next request)
```

## Migration Plan

New migration `002_add_auth_fields.py`:
1. Add `password_hash` column to `users` (nullable).
2. Add `is_active` column to `users` (default `true`).
3. Create `oauth_identities` table.
