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

## Auth Setup

### 1. Google OAuth credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new OAuth 2.0 Client ID (Web application)
3. Add `http://localhost:8000/auth/google/callback` to Authorized redirect URIs
4. Copy the Client ID and Client Secret to `api/.env`:
   ```
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

### 2. JWT secret

Generate a random secret:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Add to `api/.env`:
```
JWT_SECRET=<generated-value>
```

### 3. Apply migrations
```bash
cd api
alembic upgrade head
```

### 4. Restart backend
```bash
uvicorn app.main:app --reload --port 8000
```

## Verification

- `GET /health` → `{"success": true, "data": {"status": "ok"}}`
- Frontend renders welcome page at `http://localhost:3000`
- Swagger UI at `http://localhost:8000/docs`
- Sign up at `http://localhost:3000/register`
- Sign in at `http://localhost:3000/login`
- Sign in with Google on the login page
