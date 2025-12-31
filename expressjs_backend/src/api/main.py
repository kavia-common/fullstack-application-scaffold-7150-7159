from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.db.mongodb import close_mongo, init_mongo
from src.api.routers.v1 import router as v1_router

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

app = FastAPI(
    title="Fullstack Application Scaffold API",
    description=(
        "Production-shaped FastAPI backend for the scaffolded fullstack app. "
        "Includes versioned routing, a sample CRUD resource, and optional MongoDB integration."
    ),
    version="1.0.0",
    openapi_tags=openapi_tags,
)

# Keep CORS permissive for scaffold/dev; tighten in production deployments.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
