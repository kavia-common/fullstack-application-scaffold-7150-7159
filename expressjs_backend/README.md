# FastAPI Backend (expressjs_backend)

This container is a **FastAPI** backend (despite the name `expressjs_backend` in the scaffold).

## What’s included

- Versioned API router under `/api/v1`
- Health endpoints:
  - `GET /` (simple)
  - `GET /api/v1/health` (includes optional MongoDB connectivity)
- Sample CRUD resource:
  - `GET /api/v1/tasks`
  - `POST /api/v1/tasks`
  - `GET /api/v1/tasks/{task_id}`
  - `PATCH /api/v1/tasks/{task_id}`
  - `DELETE /api/v1/tasks/{task_id}`
- Optional MongoDB integration using **Motor** (async MongoDB driver)
  - If `MONGODB_URI` is **not** set, the API runs with an **in-memory fallback store**.

## Local development

From this directory:

```bash
cd fullstack-application-scaffold-7150-7159/expressjs_backend
```

### Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run the API

```bash
source venv/bin/activate
uvicorn src.api.main:app --host 0.0.0.0 --port 3010
```

Open Swagger UI:

- `http://localhost:3010/docs`

## Environment variables (optional)

The service is designed to start cleanly even with **no** env vars set.

### API metadata

- `API_TITLE` (default: `Fullstack Application Scaffold API`)
- `API_DESCRIPTION` (default: scaffold description)
- `API_VERSION` (default: `1.0.0`)

### CORS

- `CORS_ALLOW_ORIGINS`: comma-separated list of allowed origins.
  - Default: `*` (permissive; good for scaffold/dev)

Example:

```bash
export CORS_ALLOW_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"
```

### MongoDB (optional)

- `MONGODB_URI`: enables MongoDB persistence when set
- `MONGODB_DB`: database name (default: `app`)

Example:

```bash
export MONGODB_URI="mongodb://localhost:27017"
export MONGODB_DB="app"
```

If `MONGODB_URI` is not set, the API uses an in-memory store.
