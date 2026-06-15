# Feature Specification: User Authentication System

**Feature Branch**: `002-user-auth-system`

**Created**: 2026-06-15

**Status**: Draft

**Input**: User description: "Day 2: Auth System — Google OAuth, email/password auth, JWT sessions, login/signup pages, protected layout, profile page with plan badge"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Sign Up with Email & Password (Priority: P1)

A new visitor wants to create an account. They navigate to the signup page, enter their email and a password, and submit. The system creates their account and logs them in automatically.

**Why this priority**: Account creation is the entry point for all other features — without it, no user can use the application.

**Independent Test**: Can be fully tested by visiting `/register`, filling in email + password, submitting, and confirming redirect to the dashboard with session active.

**Acceptance Scenarios**:

1. **Given** a visitor is on the signup page, **When** they enter a valid email and password (min 8 characters) and submit, **Then** their account is created and they are redirected to the dashboard as a logged-in user.
2. **Given** a visitor submits the signup form with an email already in use, **When** the system processes the request, **Then** an error message is shown ("Email already registered") and no account is created.
3. **Given** a visitor submits the signup form with a weak password (under 8 characters), **When** the form is validated, **Then** an inline error is shown and the form is not submitted.
4. **Given** a visitor submits the signup form with an invalid email format, **When** the form is validated, **Then** an inline error is shown and the form is not submitted.

---

### User Story 2 - Sign In with Email & Password (Priority: P1)

A returning user wants to access their account. They go to the login page, enter their credentials, and are signed in.

**Why this priority**: Without login, returning users cannot access their data, making the application unusable for anyone who has signed up.

**Independent Test**: Can be fully tested by signing up, signing out, then signing in again with the same credentials and confirming access to protected pages.

**Acceptance Scenarios**:

1. **Given** a registered user is on the login page, **When** they enter correct email and password and submit, **Then** they are redirected to the dashboard as a logged-in user.
2. **Given** a user submits the login form with incorrect credentials, **When** the system validates, **Then** an error message is shown ("Invalid email or password") with no indication of which field is wrong.
3. **Given** an authenticated user navigates to the login page, **When** the page loads, **Then** they are automatically redirected to the dashboard.

---

### User Story 3 - Sign In with Google (Priority: P1)

A visitor wants to sign up or sign in using their Google account for convenience.

**Why this priority**: Google OAuth reduces friction for new users and is a widely expected sign-in option.

**Independent Test**: Can be fully tested by clicking "Sign in with Google" on the login page, completing the Google OAuth flow, and confirming the user is redirected to the dashboard as a logged-in user.

**Acceptance Scenarios**:

1. **Given** a visitor is on the login page, **When** they click "Sign in with Google" and complete the Google authorization, **Then** they are redirected to the dashboard as a logged-in user (new account created if first time, existing account linked if returning).
2. **Given** a visitor signs in with Google using an email that already has an email/password account, **When** the OAuth flow completes, **Then** the accounts are linked and the user is logged in.

---

### User Story 4 - Session Persistence Across Reload (Priority: P2)

A logged-in user refreshes their browser or closes and reopens it later. Their session should persist.

**Why this priority**: Users expect to stay logged in between sessions without re-entering credentials. Without this, the application would feel broken.

**Independent Test**: Can be fully tested by logging in, closing the browser tab, reopening the application in a new tab, and confirming the user is still authenticated.

**Acceptance Scenarios**:

1. **Given** a logged-in user refreshes the page, **When** the page reloads, **Then** the user is still authenticated and sees the same protected content.
2. **Given** a logged-in user closes their browser and returns the next day, **When** they reopen the application, **Then** they are still authenticated (session token remains valid).

---

### User Story 5 - View Profile & Plan Badge (Priority: P2)

A logged-in user wants to see their account details and know which plan they are on.

**Why this priority**: Users need visibility into their account status and plan tier. The plan badge is a gateway to future upgrade flows.

**Independent Test**: Can be fully tested by logging in, navigating to the profile page, and confirming email and plan badge are displayed correctly.

**Acceptance Scenarios**:

1. **Given** a logged-in user navigates to the profile page, **When** the page loads, **Then** their email and current plan badge (e.g. "Free" or "Pro") are displayed.
2. **Given** a logged-in user navigates to any protected page, **When** the page header renders, **Then** a user menu or avatar is visible indicating they are signed in.

---

### User Story 6 - Sign Out (Priority: P2)

A logged-in user wants to end their session.

**Why this priority**: Users must be able to securely end their session, especially on shared devices.

**Independent Test**: Can be fully tested by logging in, clicking sign out, and confirming redirect to the login page with no access to protected pages.

**Acceptance Scenarios**:

1. **Given** a logged-in user clicks "Sign Out", **When** the action is confirmed, **Then** their session is terminated and they are redirected to the login page.
2. **Given** a signed-out user tries to navigate to a protected page URL directly, **When** the page loads, **Then** they are redirected to the login page instead.

---

### Edge Cases

- What happens when Google OAuth returns an email that already belongs to an existing email/password account? Accounts should be linked.
- What happens when the session token expires while the user is mid-action? They should be redirected to login with a "Session expired" message.
- What happens if Google OAuth is temporarily unavailable? The email/password login should still work; the Google button should show an error message.
- How does the system handle concurrent sessions from different browsers? Multiple sessions for the same user should be allowed.
- What happens when a user tries to access the signup page while already logged in? They should be redirected to the dashboard.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to create an account using their email and a password.
- **FR-002**: The system MUST validate that passwords are at least 8 characters and emails are properly formatted.
- **FR-003**: Users MUST be able to sign in using their email and password.
- **FR-004**: Users MUST be able to sign in using their Google account.
- **FR-005**: The first user to sign up MUST automatically receive admin privileges.
- **FR-006**: All new accounts MUST start with the "Free" plan and zero analyses used this month.
- **FR-007**: Authenticated sessions MUST persist across page reloads and browser restarts (within token expiry).
- **FR-008**: Users MUST be able to sign out, which immediately invalidates their session.
- **FR-009**: Protected pages MUST redirect unauthenticated users to the login page.
- **FR-010**: Users MUST see their email and plan badge on a profile page.
- **FR-011**: The system MUST return errors in a consistent format for all auth failures (invalid credentials, expired sessions, duplicate registration).
- **FR-012**: The system MUST accept requests from the frontend origin and reject requests from unknown origins.

### Key Entities *(include if feature involves data)*

- **User**: Represents a person with an account. Contains email, plan tier (free/pro), analyses-used counter, admin flag, and linked OAuth identities. Created during signup or first Google login.
- **Session**: Represents an active authenticated session linked to a User. Contains a token, creation time, and expiry time. Created on login, destroyed on logout or expiry.
- **OAuth Identity**: Links a third-party provider account (e.g. Google) to a User. Contains the provider name and the user's ID on that provider. Allows users to sign in with multiple methods.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new user can complete signup and reach the dashboard in under 30 seconds.
- **SC-002**: A returning user can complete login and reach the dashboard in under 10 seconds.
- **SC-003**: Session persists for at least 7 days without requiring re-authentication.
- **SC-004**: 100% of auth-related errors return a clear, user-friendly message (no stack traces or technical jargon exposed).
- **SC-005**: Google OAuth login completes successfully on first attempt for 95% of users who have a Google account.
- **SC-006**: Unauthenticated users are blocked from accessing any protected page — all protected page requests redirect to login.

## Assumptions

- Users have a working email address and internet connection.
- Users who choose Google OAuth have a Google account.
- Google OAuth credentials (client ID, client secret) will be configured via environment variables — no admin UI for managing OAuth apps.
- The frontend and backend run on different origins during development (localhost:3000 and localhost:8000), requiring CORS support.
- Session tokens are stored securely such that JavaScript in the browser cannot read them, preventing XSS-based token theft.
- Email verification on signup is deferred to a future iteration — accounts are usable immediately after registration.
- Password reset flow is out of scope for this feature and will be addressed separately if needed.
- Rate limiting on auth endpoints is deferred to a future iteration.
