# Exam DNA SaaS

SaaS platform for exam analysis and insights.

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

### 3. Frontend

```bash
cd web
npm install
npm run dev
```

Expected: Dev server at `http://localhost:3000` showing the welcome page.

## Verification

- `GET /health` → `{"success": true, "data": {"status": "ok"}}`
- Frontend renders welcome page at `http://localhost:3000`
- Swagger UI at `http://localhost:8000/docs`
