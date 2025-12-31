"""Repository for Tasks, with MongoDB (Motor) + in-memory fallback."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.api.models.tasks import TaskCreate, TaskOut, TaskUpdate


def _now_utc() -> datetime:
    return datetime.now(tz=UTC)


def _serialize_task(doc: Dict[str, Any]) -> TaskOut:
    return TaskOut(
        id=str(doc["_id"]),
        title=doc["title"],
        description=doc.get("description"),
        completed=bool(doc.get("completed", False)),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


class InMemoryTasksStore:
    """Minimal in-memory store (used when MongoDB isn't configured)."""

    def __init__(self) -> None:
        self._items: Dict[str, Dict[str, Any]] = {}

    async def list(self, limit: int, offset: int) -> List[TaskOut]:
        values = list(self._items.values())
        values.sort(key=lambda x: x["created_at"], reverse=True)
        return [_serialize_task(v) for v in values[offset : offset + limit]]

    async def create(self, payload: TaskCreate) -> TaskOut:
        task_id = str(uuid.uuid4())
        now = _now_utc()
        doc = {
            "_id": task_id,
            "title": payload.title,
            "description": payload.description,
            "completed": payload.completed,
            "created_at": now,
            "updated_at": now,
        }
        self._items[task_id] = doc
        return _serialize_task(doc)

    async def get(self, task_id: str) -> TaskOut:
        if task_id not in self._items:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return _serialize_task(self._items[task_id])

    async def update(self, task_id: str, payload: TaskUpdate) -> TaskOut:
        if task_id not in self._items:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        doc = self._items[task_id]
        if payload.title is not None:
            doc["title"] = payload.title
        if payload.description is not None:
            doc["description"] = payload.description
        if payload.completed is not None:
            doc["completed"] = payload.completed

        doc["updated_at"] = _now_utc()
        self._items[task_id] = doc
        return _serialize_task(doc)

    async def delete(self, task_id: str) -> None:
        if task_id not in self._items:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        del self._items[task_id]


class MongoTasksStore:
    """Mongo-backed tasks store."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._col = db["tasks"]

    async def ensure_indexes(self) -> None:
        # Indexes are best-effort; do not hard-fail app startup.
        try:
            await self._col.create_index("created_at")
            await self._col.create_index("updated_at")
        except Exception:
            pass

    async def list(self, limit: int, offset: int) -> List[TaskOut]:
        cursor = self._col.find({}).sort("created_at", -1).skip(offset).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [_serialize_task(d) for d in docs]

    async def create(self, payload: TaskCreate) -> TaskOut:
        task_id = str(uuid.uuid4())
        now = _now_utc()
        doc = {
            "_id": task_id,
            "title": payload.title,
            "description": payload.description,
            "completed": payload.completed,
            "created_at": now,
            "updated_at": now,
        }
        await self._col.insert_one(doc)
        return _serialize_task(doc)

    async def get(self, task_id: str) -> TaskOut:
        doc = await self._col.find_one({"_id": task_id})
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return _serialize_task(doc)

    async def update(self, task_id: str, payload: TaskUpdate) -> TaskOut:
        update_doc: Dict[str, Any] = {"updated_at": _now_utc()}
        if payload.title is not None:
            update_doc["title"] = payload.title
        if payload.description is not None:
            update_doc["description"] = payload.description
        if payload.completed is not None:
            update_doc["completed"] = payload.completed

        result = await self._col.update_one({"_id": task_id}, {"$set": update_doc})
        if result.matched_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        doc = await self._col.find_one({"_id": task_id})
        # doc must exist because matched_count>0
        return _serialize_task(doc)  # type: ignore[arg-type]

    async def delete(self, task_id: str) -> None:
        result = await self._col.delete_one({"_id": task_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


_in_memory_store = InMemoryTasksStore()


# PUBLIC_INTERFACE
def get_tasks_store(db: Optional[AsyncIOMotorDatabase]) -> InMemoryTasksStore | MongoTasksStore:
    """Get a tasks store; uses MongoDB when configured, otherwise in-memory."""
    if db is None:
        return _in_memory_store
    return MongoTasksStore(db)
