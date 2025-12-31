"""Integration tests for /api/v1/tasks CRUD.

These tests run entirely in-process against the FastAPI ASGI app using httpx's
ASGITransport. They intentionally do not require MongoDB.

Note: In httpx>=0.28, ASGITransport is async-only, so we test via AsyncClient.
"""

from __future__ import annotations

import os
from typing import Any, Dict

import httpx
import pytest

from src.api.main import app


def _create_payload() -> Dict[str, Any]:
    return {"title": "Test task", "description": "Hello", "completed": False}


@pytest.mark.anyio
async def test_tasks_crud_end_to_end_in_memory() -> None:
    """CRUD should work end-to-end when MongoDB is not configured/reachable."""
    # Ensure MongoDB is not used for this test (in-memory fallback).
    os.environ.pop("MONGODB_URI", None)

    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Create
        r = await client.post("/api/v1/tasks", json=_create_payload())
        assert r.status_code == 200
        created = r.json()
        assert created["id"]
        assert created["title"] == "Test task"
        task_id = created["id"]

        # List
        r = await client.get("/api/v1/tasks")
        assert r.status_code == 200
        items = r.json()
        assert isinstance(items, list)
        assert any(t["id"] == task_id for t in items)

        # Get
        r = await client.get(f"/api/v1/tasks/{task_id}")
        assert r.status_code == 200
        got = r.json()
        assert got["id"] == task_id

        # Patch
        r = await client.patch(f"/api/v1/tasks/{task_id}", json={"completed": True})
        assert r.status_code == 200
        updated = r.json()
        assert updated["completed"] is True

        # Delete
        r = await client.delete(f"/api/v1/tasks/{task_id}")
        assert r.status_code == 200
        assert r.json()["deleted"] is True

        # Get after delete -> 404
        r = await client.get(f"/api/v1/tasks/{task_id}")
        assert r.status_code == 404
