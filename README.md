# fullstack-application-scaffold-7150-7159

## Backend (FastAPI)

The backend lives in:

- `expressjs_backend/` (FastAPI, despite the name)

Quick start:

```bash
cd fullstack-application-scaffold-7150-7159/expressjs_backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 3010
```

API docs:

- `http://localhost:3010/docs`

Optional MongoDB:

- Set `MONGODB_URI` to enable Mongo persistence. Otherwise the API runs with an in-memory fallback.
- See `expressjs_backend/README.md` for details.
