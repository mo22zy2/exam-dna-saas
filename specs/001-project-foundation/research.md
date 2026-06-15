# Research: Project Foundation

## Testing Framework Choice

- **Decision**: pytest for backend, vitest for frontend
- **Rationale**: Industry standard for FastAPI (pytest + httpx) and
  Next.js (vitest with @testing-library/react). Both are well-supported
  and familiar to the team.
- **Alternatives considered**: unittest (stdlib — less ergonomic),
  jest (slower than vitest for frontend)

## Docker Compose Configuration

- **Decision**: Single `docker-compose.yml` at repo root with two
  services (postgres, redis)
- **Rationale**: Simplest setup for local dev. Backend/frontend run
  natively (not in Docker) to preserve hot-reload DX.
- **Alternatives considered**: Dockerizing backend too — adds rebuild
  latency during development. Docker Compose for infra only is the
  standard FastAPI/Next.js pattern.

## Database Connection

- **Decision**: asyncpg vs psycopg2 (sync) — use psycopg2 for now
  (simpler setup with SQLAlchemy sync sessions). Can migrate to
  asyncpg if async endpoints are needed.
- **Rationale**: The scaffold has no async requirements. SQLAlchemy
  sync sessions with psycopg2 are the simplest path.

## Frontend Project Init

- **Decision**: Use `create-next-app` with App Router + TypeScript +
  Tailwind flags
- **Rationale**: Official recommended approach, generates canonical
  project structure with minimal boilerplate.
