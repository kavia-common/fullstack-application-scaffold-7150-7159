"""Versioned API router (v1)."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from src.api.db.mongodb import get_mongo_db, mongo_manager
from src.api.models.tasks import TaskCreate, TaskOut, TaskUpdate
from src.api.repositories.tasks_repo import MongoTasksStore, get_tasks_store

router = APIRouter(prefix="/api/v1", tags=["v1"])


def _get_db() -> Optional[AsyncIOMotorDatabase]:
    return get_mongo_db()


class HealthOut(BaseModel):
    """Health response including optional DB connectivity."""

    status: str = Field(..., description="Overall service status")
    mongodb_configured: bool = Field(..., description="Whether MONGODB_URI is configured")
    mongodb_ok: bool = Field(..., description="Whether MongoDB is reachable (ping) when configured")


@router.get(
    "/health",
    response_model=HealthOut,
    summary="Health check (v1)",
    description="Returns service health and MongoDB connectivity status (if configured).",
    operation_id="v1_health",
)
async def health_v1() -> HealthOut:
    """Return health information for the service and optional MongoDB connectivity.

    This endpoint must never fail due to transient DB issues. If MongoDB is
    configured but unreachable, we return mongodb_ok=False.
    """
    db = get_mongo_db()
    configured = db is not None

    ok = False
    if configured:
        try:
            ok = await mongo_manager.ping()
        except Exception:
            ok = False

    return HealthOut(status="ok", mongodb_configured=configured, mongodb_ok=ok)


@router.get(
    "/tasks",
    response_model=List[TaskOut],
    summary="List tasks",
    description="List tasks ordered by creation time (desc). Supports pagination.",
    operation_id="v1_tasks_list",
    tags=["tasks"],
)
async def list_tasks(
    limit: int = Query(50, ge=1, le=200, description="Max number of tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
    db: Optional[AsyncIOMotorDatabase] = Depends(_get_db),
) -> List[TaskOut]:
    """List tasks."""
    store = get_tasks_store(db)
    # Ensure indexes when using Mongo store (best-effort, idempotent).
    if isinstance(store, MongoTasksStore):
        await store.ensure_indexes()
    return await store.list(limit=limit, offset=offset)


@router.post(
    "/tasks",
    response_model=TaskOut,
    summary="Create task",
    description="Create a new task.",
    operation_id="v1_tasks_create",
    tags=["tasks"],
)
async def create_task(
    payload: TaskCreate,
    db: Optional[AsyncIOMotorDatabase] = Depends(_get_db),
) -> TaskOut:
    """Create a task."""
    store = get_tasks_store(db)
    return await store.create(payload)


@router.get(
    "/tasks/{task_id}",
    response_model=TaskOut,
    summary="Get task",
    description="Retrieve a single task by its id.",
    operation_id="v1_tasks_get",
    tags=["tasks"],
)
async def get_task(
    task_id: str,
    db: Optional[AsyncIOMotorDatabase] = Depends(_get_db),
) -> TaskOut:
    """Get a task by id."""
    store = get_tasks_store(db)
    return await store.get(task_id)


@router.patch(
    "/tasks/{task_id}",
    response_model=TaskOut,
    summary="Update task",
    description="Partially update a task by its id.",
    operation_id="v1_tasks_update",
    tags=["tasks"],
)
async def update_task(
    task_id: str,
    payload: TaskUpdate,
    db: Optional[AsyncIOMotorDatabase] = Depends(_get_db),
) -> TaskOut:
    """Update a task by id."""
    store = get_tasks_store(db)
    return await store.update(task_id, payload)


@router.delete(
    "/tasks/{task_id}",
    summary="Delete task",
    description="Delete a task by its id.",
    operation_id="v1_tasks_delete",
    tags=["tasks"],
)
async def delete_task(
    task_id: str,
    db: Optional[AsyncIOMotorDatabase] = Depends(_get_db),
) -> dict:
    """Delete a task by id."""
    store = get_tasks_store(db)
    await store.delete(task_id)
    return {"deleted": True, "id": task_id}
