# Feature Specification: R2 Upload Storage

**Feature Branch**: `004-r2-upload-storage`

**Created**: 2026-06-16

**Status**: Draft

**Input**: User description: "Day 4: FastAPI Upload Endpoint + R2 Storage + Rate Limiting"

## Clarifications

### Session 2026-06-16

- Q: When does file content type validation happen relative to secure upload token issuance? → A: Post-upload verification — token is issued after limit checks only; content validation happens as a separate step after the file reaches storage. Invalid files are quarantined or flagged.
- Q: What states do uploaded files progress through? → A: Three states: uploaded (stored, pending check) → validated (content check passed) → available (ready for analysis) OR rejected (failed content check, quarantined).
- Q: What signals the end of an upload session? → A: Inactivity timeout — session remains open while the user continues uploading; it automatically closes after 30 minutes of inactivity from the last file upload.
- Q: Is file listing part of this feature or a separate feature? → A: In scope — a basic file listing capability (list user's uploaded files with metadata) is included in this feature. Minimal: list only, no delete/search/filter.
- Q: How does the system handle duplicate filenames from the same user? → A: Allow duplicates — multiple files can share the same filename, distinguished by upload timestamp and other metadata. The system uses a unique internal identifier, not the filename, for references.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload exam files securely (Priority: P1)

As an authenticated user on the free tier, I want to upload exam files so that I can later analyze them. The system should validate file types by inspecting file content (not just the extension), enforce usage limits, and protect against abuse through rate limiting.

**Why this priority**: File upload is the foundational capability that all downstream features (analysis, viewing) depend on. Without it, no other functionality is possible.

**Independent Test**: A user can authenticate, upload a valid PDF file, receive a success confirmation, and see the file listed with its metadata.

**Acceptance Scenarios**:

1. **Given** I am an authenticated user, **When** I upload a valid PDF file, **Then** the system accepts the file and returns a success confirmation with the file's metadata (name, size, type, upload date).
2. **Given** I am an authenticated user, **When** I upload a file whose content does not match its claimed type (e.g., a renamed executable), **Then** the system rejects it with a clear error message.
3. **Given** I am an authenticated user, **When** I exceed the upload rate limit, **Then** the system rejects subsequent uploads with a message indicating when I can retry.
4. **Given** I have reached my free tier limit of 20 stored files, **When** I attempt to upload another file, **Then** the system rejects the upload with a message explaining the limit.
5. **Given** I am not authenticated, **When** I attempt to upload a file, **Then** the system rejects the request.

---

### User Story 2 - Upload large files reliably (Priority: P2)

As an authenticated user, I want to upload large exam files without the upload timing out or being interrupted by server processing limits. The upload should happen directly from my browser to the storage service.

**Why this priority**: Direct browser uploads improve reliability for larger files and reduce server load, but the basic upload-to-server flow (Story 1) can be implemented first as a fallback.

**Independent Test**: A user uploads a file from the browser, and it is stored in the cloud storage without the file data passing through the application server, then the file appears in their list.

**Acceptance Scenarios**:

1. **Given** I have passed the free tier checks, **When** the system issues a secure upload token, **Then** the token expires after 15 minutes for security.
2. **Given** I have a valid upload token, **When** I upload directly to storage, **Then** the file is stored without passing through the application server.
3. **Given** I try to upload using an expired token, **Then** the upload is rejected.

---

### User Story 3 - Track upload sessions (Priority: P3)

As an authenticated user uploading multiple files, I want all my related uploads grouped together so that I can manage and analyze them as a collection.

**Why this priority**: Session grouping improves organization and enables batch analysis flows, but individual file upload works independently without it.

**Independent Test**: A user uploads three files and all three are associated with the same session in their file list.

**Acceptance Scenarios**:

1. **Given** I start uploading files, **When** the first file is validated successfully, **Then** an upload session is created to group subsequent files.
2. **Given** I upload multiple files, **When** I view my uploaded files, **Then** all files in the same session are identifiable as a group.
3. **Given** I upload a file, **When** no active session exists, **Then** a new session is automatically created for that file.

---

### Edge Cases

- What happens when a user uploads a corrupted file that passes content inspection but is otherwise unreadable? The system accepts it (content type is valid), but downstream processing should handle gracefully.
- How does the system handle upload tokens that were issued but never used? The associated token expires after 15 minutes per FR-005; any session with no files uploaded within 30 minutes of inactivity is automatically closed.
- What happens when the storage service is unreachable? The system returns a clear error and does not count the failed attempt against the user's file quota.
- How does the system handle concurrent uploads from the same user? Rate limiting prevents excessive requests, and the system gracefully queues or rejects beyond-limit attempts.
- What happens when a file uploaded via direct URL fails post-upload content validation? The file remains in storage but is flagged as invalid, the user is notified, and the file does not count toward storage quota or become available for analysis.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST validate file type by inspecting file content (not relying solely on file extension). For direct browser uploads, validation happens as a post-upload step after the file reaches storage; files that fail validation MUST be quarantined or flagged and not made available for use.
- **FR-002**: System MUST enforce a rate limit of 10 upload attempts per minute per authenticated user, returning a clear message when the limit is exceeded.
- **FR-003**: System MUST verify that the user has not reached the free tier limit of 20 stored files before authorizing any upload.
- **FR-004**: System MUST verify that the user has not exceeded the monthly analysis quota (1 per month) before authorizing any upload, using a counter maintained separately.
- **FR-005**: System MUST generate time-limited upload tokens that expire 15 minutes after issuance, preventing unauthorized or stale upload attempts.
- **FR-006**: System MUST create a session record when the first file in a logical upload flow is accepted and associate all subsequent files in that flow with the same session.
- **FR-007**: System MUST persist file metadata (original filename, size, detected type, upload timestamp, session identifier, storage reference) after a successful upload.
- **FR-008**: System MUST return a confirmation response containing file metadata upon successful upload.
- **FR-009**: System MUST reject all upload requests from unauthenticated users.
- **FR-010**: System MUST provide authenticated users with the ability to list their uploaded files and view metadata (filename, size, type, upload date, session, validation status) for each file.

### Key Entities *(include if feature involves data)*

- **FileRecord**: Represents a single uploaded file. Identified internally by a unique system-generated identifier (not the filename). Contains metadata such as original filename, file size, detected file type, upload timestamp, storage reference, session association, and lifecycle state (uploaded, validated, available, rejected). Multiple files with the same original filename from the same user are allowed.
- **UploadSession**: Represents a logical grouping of one or more file uploads. Created automatically when a file is accepted and no active session exists. Automatically closed after 30 minutes of inactivity following the last file upload. Tracks creation time, last activity, and associated files.
- **UserQuota**: Tracks per-user counts for stored files and monthly analysis usage. Used to enforce free tier limits before authorizing uploads.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can upload a valid file and receive a success confirmation with metadata within 5 seconds (excluding file transfer time).
- **SC-002**: Files with non-matching content types are detected with 100% accuracy through post-upload content inspection and are never made available for analysis or further use, regardless of file extension.
- **SC-003**: Users who exceed the rate limit receive a clear message and can resume uploading once the rate window resets.
- **SC-004**: Users at the 20-file storage limit receive a clear message and cannot upload until they free capacity.
- **SC-005**: Upload tokens older than 15 minutes cannot be used to store files.
- **SC-006**: Successfully uploaded files appear in the user's file list with correct metadata within 10 seconds of upload completion.
- **SC-007**: Every file upload is associated with exactly one UploadSession record.
- **SC-008**: Free tier limit checks are performed before any upload authorization, preventing over-limit uploads.

## Assumptions

- The supported file format for this feature is PDF; additional document formats may be supported in future iterations.
- Files up to typical exam document sizes (under 100MB) are supported; larger files may need special handling in the future.
- Users have a stable internet connection sufficient for uploading exam files.
- The existing authentication system is used to identify users for rate limiting and quota enforcement.
- The monthly analysis quota is maintained as a counter that the separate analysis feature increments; this feature only reads the counter to enforce the limit.
- Storage infrastructure is provisioned and accessible as a prerequisite.
- Upload sessions are created server-side at the time the first file is accepted, not by the client.
- Stale sessions (no files uploaded within 24 hours) can be cleaned up by a background process.
