# Data Model: Project Foundation

## Entity-Relationship Diagram (text)

```
User 1───* UploadSession 1───* File
```

## User

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, default uuid4 | |
| email | String(255) | NOT NULL, UNIQUE, indexed | |
| plan | String(20) | NOT NULL, default 'free' | 'free' or 'pro' |
| analyses_used_this_month | Integer | NOT NULL, default 0 | Counter, reset monthly |
| is_admin | Boolean | NOT NULL, default false | |
| created_at | DateTime(timezone=True) | NOT NULL, default now | |
| updated_at | DateTime(timezone=True) | NOT NULL, onupdate now | |

### Validation Rules
- `email` must match email format (Pydantic validation)
- `plan` limited to `'free'` or `'pro'`
- `analyses_used_this_month` >= 0

## UploadSession

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, default uuid4 | |
| user_id | UUID | FK → User.id, NOT NULL, indexed | |
| status | String(20) | NOT NULL, default 'pending' | pending/processing/completed/failed |
| created_at | DateTime(timezone=True) | NOT NULL, default now | |
| updated_at | DateTime(timezone=True) | NOT NULL, onupdate now | |

### Validation Rules
- `status` must be one of: pending, processing, completed, failed
- `user_id` must reference an existing User

## File

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, default uuid4 | |
| upload_session_id | UUID | FK → UploadSession.id, NOT NULL, indexed | |
| filename | String(255) | NOT NULL | Original filename |
| storage_key | String(512) | NOT NULL | Object store path/key |
| file_size | Integer | NOT NULL | Size in bytes |
| created_at | DateTime(timezone=True) | NOT NULL, default now | |

### Validation Rules
- `file_size` >= 0
- `upload_session_id` must reference an existing UploadSession

## Indexes

- User: `email` (unique)
- UploadSession: `user_id`, `status`
- File: `upload_session_id`
