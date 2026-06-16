# Data Model: R2 Upload Storage

## Entities

### FileRecord (Table: `files`)

Represents a single uploaded file. Extends the existing `File` model from 003-file-upload-ui.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, default uuid4 | System-generated unique identifier |
| `user_id` | UUID | FK → users.id, NOT NULL, indexed | Owner of the file |
| `upload_session_id` | UUID | FK → upload_sessions.id, NULLABLE | Session this file belongs to |
| `filename` | String(255) | NOT NULL | Original filename from upload |
| `storage_key` | String(512) | NOT NULL, UNIQUE | R2 object key (e.g., `users/{user_id}/{file_id}.pdf`) |
| `file_size` | Integer | NOT NULL | Size in bytes |
| `classification` | String(20) | NOT NULL | "exam" or "lecture" (from existing 003 feature) |
| `mime_type` | String(50) | NOT NULL, default "application/pdf" | Detected MIME type from python-magic |
| `status` | String(20) | NOT NULL, default "uploaded" | Lifecycle state (see below) |
| `validation_status` | String(20) | NOT NULL, default "pending" | **NEW**: pending, validated, rejected |
| `created_at` | DateTime(tz) | NOT NULL | Upload timestamp |
| `updated_at` | DateTime(tz) | NOT NULL, onupdate | Last modification timestamp |

**Relationships**:
- `user` → User (many-to-one): A user has many files
- `upload_session` → UploadSession (many-to-one): A session groups many files

**Validation rules per spec**:
- FR-001: `mime_type` must be `application/pdf` after content validation (files with other types are `rejected`)
- FR-003: User must have < 20 files with status != `rejected` before issuing presigned URL
- FR-007: All metadata fields must be populated on successful upload
- Duplicate filenames allowed (identified by `id`, not `filename`)

**Lifecycle states** (`status` field):

```
uploaded ──→ validated ──→ available
                          ↘ rejected
```

| State | Meaning |
|-------|---------|
| `uploaded` | File stored in R2, pending content validation (post-upload) |
| `validated` | Content check passed (python-magic confirmed PDF) |
| `available` | Fully processed and ready for analysis |
| `rejected` | Content check failed; file quarantined, not usable |

---

### UploadSession (Table: `upload_sessions`)

Represents a logical grouping of file uploads. Extends the existing `UploadSession` model.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, default uuid4 | System-generated unique identifier |
| `user_id` | UUID | FK → users.id, NOT NULL, indexed | Session owner |
| `status` | String(20) | NOT NULL, default "open" | open, closed |
| `file_count` | Integer | NOT NULL, default 0 | Number of files in this session |
| `last_activity` | DateTime(tz) | NOT NULL | **NEW**: timestamp of last file upload in this session, used for 30-min inactivity timeout |
| `created_at` | DateTime(tz) | NOT NULL | Session creation timestamp |
| `updated_at` | DateTime(tz) | NOT NULL, onupdate | Last modification timestamp |

**Relationships**:
- `user` → User (many-to-one): A user has many sessions
- `files` → FileRecord (one-to-many): A session has many files

**Behavior per spec**:
- FR-006: Created automatically when the first file is accepted and no open session exists
- Session auto-closes after 30 minutes of inactivity (last_activity)
- A new session is created if the user uploads after the previous one closed

---

### UserQuota (Conceptual — enforced via User model counter)

Not a separate table. Tracks per-user limits using existing or new columns on the `users` table.

| Field | Type | Description |
|-------|------|-------------|
| `files_uploaded` | Integer (existing) | Total stored files (excluding rejected) |
| `analyses_count` | Integer | **NEW**: Monthly analysis usage counter; incremented by analysis feature, read by this feature for enforcement |

**Enforcement per spec**:
- FR-003: Before issuing presigned URL, check `files_uploaded < 20`
- FR-004: Before issuing presigned URL, check `analyses_count < 1` for current month

---

## Entity Relationship Diagram (text)

```
User (users)
  │
  ├── files_uploaded: int (existing)
  ├── analyses_count: int (NEW, monthly counter)
  │
  ├──< UploadSession (upload_sessions)
  │     ├── id: UUID
  │     ├── user_id: UUID FK
  │     ├── status: "open" | "closed"
  │     ├── file_count: int
  │     └── last_activity: datetime
  │
  └──< FileRecord (files)
        ├── id: UUID
        ├── user_id: UUID FK
        ├── upload_session_id: UUID FK?
        ├── filename: string
        ├── storage_key: string (UNIQUE)
        ├── file_size: int
        ├── classification: "exam" | "lecture"
        ├── mime_type: string
        ├── status: lifecycle state
        ├── validation_status: "pending" | "validated" | "rejected"
        └── created_at, updated_at: datetime
```

## Migration Plan

Based on the existing models from 003-file-upload-ui:

1. **files table**: Add `validation_status` column (String(20), default "pending")
2. **upload_sessions table**: Add `last_activity` column (DateTime(tz), default now)
3. **users table**: Add `analyses_count` column (Integer, default 0) + `analyses_month` to track which month the count is for, OR a simpler approach: reset count on first-of-month check
4. Remove the existing local `uploads/` storage directory migration (files already in R2)
