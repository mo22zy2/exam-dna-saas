# API Contracts: Project Foundation

## Health Check

### `GET /health`

Returns service health status.

**Response `200`**:
```json
{
  "success": true,
  "data": {
    "status": "ok"
  }
}
```

**Response `503`** (if DB unavailable):
```json
{
  "success": false,
  "error": "Service unavailable"
}
```

## OpenAPI Schema

All future endpoints will use FastAPI's auto-generated OpenAPI docs
at `/docs` (served at `http://localhost:8000/docs` in development).
