# Feature Specification: File Upload UI & Validation

**Feature Branch**: `003-file-upload-ui`

**Created**: 2026-06-15

**Status**: Draft

**Input**: User description: "Day 3: File Upload UI + Validation - Install react-dropzone (Next.js), Build upload page layout, Filter for PDF only — extension AND magic bytes (client-side check via file-type JS lib), Enforce 50MB size limit (client-side), File list: names + sizes, Upload progress bar (per file), Classify files: 'Exam' or 'Lecture' tag, Show free-tier limit on UI (e.g. '3/3 files used'), Upload button -> calls FastAPI endpoint"

## Clarifications

### Session 2026-06-15

- Q: Should multiple selected files upload in parallel or sequentially? → A: Sequential upload with queue — one file uploads at a time; remaining files wait in a visible queue with per-file status (pending, uploading, completed, failed).
- Q: How should duplicate filenames be handled? → A: Auto-rename with suffix (e.g., `report (1).pdf`) for storage; original filename displayed in the file list.
- Q: Is there a maximum number of files per batch selection? → A: Cap at 10 files per batch selection.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload a PDF with Classification (Priority: P1)

A user navigates to the upload page, selects a PDF file, chooses whether it is an Exam or a Lecture, and uploads it. The system validates the file (type and size), shows upload progress, and confirms success.

**Why this priority**: Uploading files is the primary action this feature supports — without it, users cannot bring their documents into the system for analysis.

**Independent Test**: Can be fully tested by navigating to the upload page, selecting a valid PDF under 50MB, picking a classification tag (Exam or Lecture), clicking upload, and confirming the file appears in the file list with the correct tag.

**Acceptance Scenarios**:

1. **Given** a user is on the upload page, **When** they select a valid PDF file under 50MB, assign it an "Exam" tag, and click upload, **Then** a progress bar shows the upload advancing and the file appears in the file list with its name, size, and "Exam" tag.
2. **Given** a user selects a valid PDF file under 50MB with a "Lecture" tag and uploads, **Then** the file appears in the file list with the "Lecture" tag.
3. **Given** a user tries to upload a file without selecting a classification tag, **When** they click upload, **Then** the action is not allowed and a prompt asks them to select Exam or Lecture.
4. **Given** a user drops a non-PDF file onto the upload area, **When** the system inspects the file, **Then** the file is rejected immediately with a clear message stating that only PDF files are accepted.

---

### User Story 2 - Understand Free-Tier Limits (Priority: P2)

A free-tier user wants to know how many files they can still upload. The UI shows their usage and remaining capacity both before and after uploads.

**Why this priority**: Transparent limits prevent frustration and reduce surprise rejections, which is critical for user trust and retention.

**Independent Test**: Can be fully tested by checking that the upload page displays the current file count and limit (e.g. "2/3 files used"), uploading a file, and confirming the counter updates to "3/3 files used".

**Acceptance Scenarios**:

1. **Given** a free-tier user is on the upload page, **When** the page loads, **Then** the remaining upload capacity is displayed (e.g. "2 of 3 files used").
2. **Given** a free-tier user has reached their file limit, **When** they attempt to upload another file, **Then** the upload is rejected with a message explaining the limit has been reached.

---

### User Story 3 - View and Manage Uploaded Files (Priority: P3)

A user wants to see all their previously uploaded files in a list, with their names, sizes, and classification tags visible at a glance.

**Why this priority**: After uploading, users need to confirm their files are present and correctly tagged before proceeding to analysis.

**Independent Test**: Can be fully tested by uploading two files (one Exam, one Lecture) and confirming the file list shows both with correct names, sizes, and tags.

**Acceptance Scenarios**:

1. **Given** a user has uploaded several files, **When** they view the file list, **Then** each file displays its name, size (in human-readable format), and classification tag.
2. **Given** a user has no uploaded files, **When** they view the upload page, **Then** a helpful empty state message is shown (e.g. "No files uploaded yet").

---

### Edge Cases

- What happens when a user uploads a file with a .pdf extension but the content is not actually a PDF? The system must reject it based on content inspection, not just the filename extension.
- What happens when a user tries to upload a file exactly at the 50MB size limit? The file should be accepted (boundary condition).
- What happens when a user tries to upload a file that exceeds 50MB? The file is rejected immediately with a clear size-limit message.
- What happens when network connectivity is lost during an upload? The upload should fail gracefully, the progress bar should indicate failure, and the user should be able to retry.
- What happens when a free-tier user upgrades to a paid plan mid-session? The limit display should update to reflect the new allocation.
- What happens when a user uploads a file with the same name as an existing file? The system auto-renames the new file by appending a numeric suffix (e.g., `report (1).pdf`) for storage; the original filename is still displayed in the file list.
- What happens when a user selects a file and then changes their mind? They should be able to remove a file from the selection list before uploading.
- What happens when a user wants to reorder or cancel files waiting in the upload queue before their turn? The queue should allow removing pending items; reordering is not required.
- What happens when a user selects more than 10 files at once? The selection is capped at 10 — additional files beyond the limit are ignored with a notification.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to select up to 10 PDF files per batch for upload from their local device.
- **FR-002**: The system MUST validate uploaded files are genuine PDFs by inspecting both the file extension and the file content (magic bytes), rejecting any file that fails either check.
- **FR-003**: The system MUST reject any file that exceeds 50 MB in size before the upload begins.
- **FR-004**: Users MUST assign a classification tag ("Exam" or "Lecture") to each file before uploading.
- **FR-005**: When multiple files are selected, the system MUST upload them sequentially (one at a time). A queue shows all selected files with per-file status (pending, uploading, completed, failed). The currently uploading file displays a progress bar with percentage complete.
- **FR-006**: The system MUST display a list of uploaded files showing each file's name, size in human-readable format, and classification tag.
- **FR-007**: The system MUST display the user's current file count and upload limit for their plan (e.g. "3/3 files used").
- **FR-008**: The system MUST enforce the user's file upload limit on the server side, preventing uploads beyond the plan allocation even if client-side checks are bypassed.
- **FR-009**: When a user reaches their upload limit, the system MUST reject further uploads with a clear message explaining the limit.
- **FR-010**: The system MUST associate each uploaded file with the authenticated user who uploaded it.
- **FR-011**: The system MUST present a clear empty state when no files have been uploaded yet.
- **FR-012**: The system MUST provide clear error messages for all rejection scenarios (wrong file type, exceeds size limit, plan limit reached, network failure).
- **FR-013**: When a user uploads a file whose name matches an existing file, the system MUST auto-rename the new file with a numeric suffix for storage while preserving the original filename display in the file list.

### Key Entities *(include if feature involves data)*

- **UploadedFile**: Represents a document uploaded by a user. Contains the original filename, file size, storage location, classification tag (Exam or Lecture), upload timestamp, and a reference to the owning User. Created on successful upload, referenced during file listing and future analysis.
- **UploadSession**: Represents the state of an active multi-file upload operation. Maintains a sequential queue of files with per-file status (pending, uploading, completed, failed) and individual progress percentages. Exists only during the upload flow and is discarded upon completion or cancellation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can select a PDF file, classify it, and complete the upload in under 30 seconds for a 10 MB file over a typical broadband connection.
- **SC-002**: Non-PDF files and files exceeding 50 MB are rejected with a clear, actionable error message 100% of the time.
- **SC-003**: Upload progress is visible to the user throughout the upload — the progress indicator updates at least every 2 seconds.
- **SC-004**: Free-tier users cannot exceed their plan's file upload limit under any circumstances — server-side enforcement blocks 100% of over-limit upload attempts.
- **SC-005**: The file list updates within 5 seconds of an upload completing, showing the new file with correct metadata.
- **SC-006**: 100% of error states (wrong type, over limit, network failure) display a user-friendly message with no technical jargon or stack traces visible.

## Assumptions

- Users have a stable internet connection suitable for uploading files up to 50 MB.
- The system backlog shows files are uploaded for subsequent analysis (PDF text extraction, question generation, etc.) — the analysis pipeline itself is out of scope for this feature.
- Free-tier users have a default limit of 3 uploaded files; paid/pro plan limits are configurable and may differ.
- The authenticated user context is already available via the existing auth system — users must be logged in to access the upload page.
- Files are classified manually by the user via a dropdown or toggle before upload — automatic classification is deferred.
- The storage backend (local disk, cloud storage, etc.) is an implementation detail abstracted from this specification.
- Uploaded files are retained indefinitely unless the user deletes their account or a future data retention policy is introduced.
