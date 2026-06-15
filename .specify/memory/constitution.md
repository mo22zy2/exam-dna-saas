<!--
  Sync Impact Report
  ========================================================================
  Version change: 0.0.0 (uninitialized template) → 1.0.0
  Modified principles (all new):
    - [PRINCIPLE_1_NAME] → I. Technology Stack
    - [PRINCIPLE_2_NAME] → II. LLM Abstraction Layer
    - [PRINCIPLE_3_NAME] → III. Input Validation
    - [PRINCIPLE_4_NAME] → IV. Server-Side Enforcement
    - [PRINCIPLE_5_NAME] → V. Job Reliability & Retry
  Added sections:
    - Development Constraints (was [SECTION_2_NAME])
    - Quality & Observability (was [SECTION_3_NAME])
    - Governance rules populated
  Removed sections: none
  Templates requiring updates:
    - ✅ .specify/templates/plan-template.md (generic Constitution Check — no change needed)
    - ✅ .specify/templates/spec-template.md (no principle-specific references)
    - ✅ .specify/templates/tasks-template.md (no principle-specific references)
    - ✅ .opencode/commands/*.md (no CLAUDE/outdated references found)
  Follow-up TODOs:
    - TODO(RATIFICATION_DATE): ask project lead for original adoption date
  ========================================================================
-->

# Exam DNA SaaS Constitution

## Core Principles

### I. Technology Stack

- **Backend**: Python/FastAPI with SQLAlchemy ORM and Alembic for
  migrations. Prisma MUST NOT be used.
- **Frontend**: Next.js (App Router) + TypeScript + Tailwind CSS.
- **Queue**: RQ (Redis Queue). Celery and BullMQ MUST NOT be used.
- **Database**: PostgreSQL (via SQLAlchemy).

Rationale: Standardizing on a single ORM, queue, and frontend framework
avoids fragmentation, reduces maintenance burden, and ensures all
contributors share a common mental model.

### II. LLM Abstraction Layer

- All LLM provider calls MUST go through the single `llm.py` abstraction
  module.
- Provider SDKs MUST NOT be called directly from any other module.
- The `llm.py` module owns prompt construction, retry logic, token
  tracking, and response parsing.

Rationale: Centralizing LLM interactions prevents provider lock-in,
enables consistent observability, and simplifies swapping providers or
models.

### III. Input Validation

- Every API endpoint MUST validate its input with Pydantic models.
- Request bodies, query parameters, and path parameters are all in scope.
- Validation errors MUST return structured error responses.

Rationale: Pydantic provides compile-time and runtime guarantees against
malformed or malicious input, eliminating an entire class of bugs.

### IV. Server-Side Enforcement

- Free-tier limits (file count, analyses per month, storage quota) MUST
  be enforced server-side, never only client-side.
- The frontend MAY display limits for UX, but the backend is the
  authoritative gate.

Rationale: Client-only checks are trivially bypassed. Server-side
enforcement is the only reliable way to protect plan boundaries.

### V. Job Reliability & Retry

- Every async RQ job MUST log errors to the `Job` database table.
- Each job MUST support automatic retry with a maximum of 3 attempts.
- After exhausting retries, the job MUST be marked as failed with the
  last error persisted.

Rationale: Asynchronous jobs are failure-prone (transient network issues,
rate limits). Logging and retry ensure observability and self-healing
without manual intervention.

## Development Constraints

- Changes MUST be scoped to the current task. Unrelated refactoring is
  prohibited in the same PR/commit.
- If a refactor is genuinely needed, it MUST be filed as a separate task
  and reviewed independently.

Rationale: Mixed-purpose changes increase review surface, raise the
risk of regressions, and make git history harder to trace.

## Quality & Observability

- All modules MUST include structured logging via the project's logging
  utility (not bare `print()` calls).
- Error handling MUST distinguish between expected (validation) and
  unexpected (system) failures.
- API responses MUST follow a consistent envelope format
  (`{success, data, error}`).

Rationale: Consistent observability patterns reduce debugging time and
make the system's behavior predictable across all layers.

## Governance

1. **Supremacy**: This constitution supersedes all other practices,
   style guides, and conventions.
2. **Amendments**: Proposed changes MUST be documented in a GitHub
   Issue or PR with rationale, migration plan (if applicable), and
   explicit version bump per semantic versioning.
3. **Versioning policy**:
   - MAJOR: Backward-incompatible governance/principle removals or
     redefinitions.
   - MINOR: New principle or section added, or materially expanded
     guidance.
   - PATCH: Clarifications, wording, typo fixes, non-semantic
     refinements.
4. **Compliance**: All PRs MUST be reviewed against this constitution
   before merge. Violations MUST be justified via the Complexity
   Tracking table in the implementation plan.
5. **Review cadence**: The constitution SHOULD be reviewed quarterly
   for continued relevance.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): ask project lead for original adoption date | **Last Amended**: 2026-06-15
