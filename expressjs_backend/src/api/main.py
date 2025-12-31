"""FastAPI application entrypoint.

This is the main ASGI entrypoint used by Uvicorn/Gunicorn:
    uvicorn src.api.main:app --host 0.0.0.0 --port 3010

Notes:
- This app intentionally loads a local `.env` file (if present) so the service can
  be started in dev/preview environments without manual `export ...`.
- All configuration remains optional; safe defaults allow clean startup even with
  no env vars set.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load `.env` as early as possible so settings/db init see environment variables.
# This is a no-op if the file is missing.
load_dotenv()

from src.api.db.mongodb import close_mongo, init_mongo
from src.api.routers.v1 import router as v1_router
from src.api.settings import get_api_metadata, get_cors_allow_origins

openapi_tags = [
    {
        "name": "health",
        "description": "Service health and readiness endpoints.",
    },
    {
        "name": "tasks",
        "description": "Sample CRUD resource used as a template for future features.",
    },
    {
        "name": "v1",
        "description": "Versioned API grouping.",
    },
]

_api_meta = get_api_metadata()

app = FastAPI(
    title=_api_meta["title"],
    description=_api_meta["description"],
    version=_api_meta["version"],
    openapi_tags=openapi_tags,
)

# Keep CORS permissive for scaffold/dev; tighten in production deployments by setting CORS_ALLOW_ORIGINS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_allow_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def _startup() -> None:
    """Initialize external resources (optional MongoDB connection)."""
    await init_mongo()


@app.on_event("shutdown")
async def _shutdown() -> None:
    """Cleanup external resources."""
    await close_mongo()


# PUBLIC_INTERFACE
@app.get(
    "/",
    tags=["health"],
    summary="Health check (root)",
    description="Simple health endpoint. For detailed status (including DB), use /api/v1/health.",
    operation_id="health_check_root",
)
def health_check() -> dict:
    """Root health endpoint for quick checks and load balancers."""
    return {"message": "Healthy"}


app.include_router(v1_router)
