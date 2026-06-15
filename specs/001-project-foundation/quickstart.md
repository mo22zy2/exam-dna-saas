# Quickstart: Project Foundation

## Prerequisites

- Docker Desktop (or compatible Docker runtime)
- Python 3.12+
- Node.js 20 LTS
- Git

## Setup

### 1. Start infrastructure

```bash
docker compose up -d
```

Expected: PostgreSQL on `localhost:5432`, Redis on `localhost:6379`.

### 2. Backend

```bash
cd api
python -m venv .venv
.venv\Scripts\activate    # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Expected: API running at `http://localhost:8000`.
Verify: `curl http://localhost:8000/health` → `{"success": true, "data": {"status": "ok"}}`
Verify: `http://localhost:8000/docs` → Swagger UI loads.

### 3. Frontend

```bash
cd web
npm install
npm run dev
```

Expected: Dev server at `http://localhost:3000` showing the welcome
page.

## Verification Checklist

- [ ] `docker compose up` starts both containers without errors
- [ ] `alembic upgrade head` runs without errors
- [ ] `alembic downgrade -1` rolls back cleanly
- [ ] Tables `users`, `upload_sessions`, `files` exist in Postgres
  (`psql -h localhost -U postgres -d examdna -c "\dt"`)
- [ ] `GET /health` returns `{"success": true, "data": {"status": "ok"}}`
- [ ] Frontend renders welcome page at `http://localhost:3000`
