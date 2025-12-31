"""
MongoDB integration layer.

This module is intentionally resilient:
- If MONGODB_URI is not provided, the API still runs and falls back to in-memory storage.
- If MongoDB is unreachable, the service must still start cleanly and CRUD should
  remain usable via the in-memory fallback.

Env vars (optional):
- MONGODB_URI: MongoDB connection string, e.g. mongodb://localhost:27017
- MONGODB_DB: Database name (default: "app")
- MONGODB_SERVER_SELECTION_TIMEOUT_MS: Bound how long the driver waits when Mongo
  is unreachable (default: 500ms). Keeping this low avoids Swagger "Try it out"
  requests hanging.
"""

from __future__ import annotations

import os
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class MongoClientManager:
    """Holds a MongoDB client + database for the lifetime of the process."""

    def __init__(self) -> None:
        self._client: Optional[AsyncIOMotorClient] = None
        self._db: Optional[AsyncIOMotorDatabase] = None

    def configure_from_env(self) -> None:
        """Configure Mongo client from environment variables, if present."""
        mongodb_uri = os.getenv("MONGODB_URI")
        db_name = os.getenv("MONGODB_DB", "app")

        if not mongodb_uri:
            # No DB configured; leave client unset so app can operate in memory.
            self._client = None
            self._db = None
            return

        # Motor client is lazy; connection is verified separately via ping.
        # IMPORTANT: bound server selection to avoid long request hangs when Mongo is down.
        timeout_ms_raw = os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "500")
        try:
            timeout_ms = max(50, int(timeout_ms_raw))
        except ValueError:
            timeout_ms = 500

        self._client = AsyncIOMotorClient(
            mongodb_uri,
            serverSelectionTimeoutMS=timeout_ms,
        )
        self._db = self._client[db_name]

    async def ping(self) -> bool:
        """Return True if MongoDB is configured and reachable, else False.

        Note: Motor/PyMongo Database objects **must not** be evaluated for truthiness
        (`if db:` / `if not db:`) because that raises NotImplementedError.
        Always compare explicitly with None.
        """
        if self._db is None:
            return False
        try:
            await self._db.command("ping")
            return True
        except Exception:
            return False

    def get_db(self) -> Optional[AsyncIOMotorDatabase]:
        """Return the configured database handle (or None if not configured)."""
        return self._db

    def disable(self) -> None:
        """Disable Mongo usage for this process (fallback to in-memory)."""
        self.close()

    def close(self) -> None:
        """Close the Mongo client if open."""
        if self._client is not None:
            self._client.close()
        self._client = None
        self._db = None


mongo_manager = MongoClientManager()


# PUBLIC_INTERFACE
async def init_mongo() -> None:
    """Initialize MongoDB connection manager from environment variables.

    If MongoDB is configured but unreachable, we disable it and allow the app to
    continue with in-memory stores so Swagger verification remains functional.
    """
    mongo_manager.configure_from_env()

    # If configured but not reachable, disable Mongo usage to prevent hangs.
    ok = await mongo_manager.ping()
    if not ok:
        mongo_manager.disable()


# PUBLIC_INTERFACE
async def close_mongo() -> None:
    """Close MongoDB resources, if any."""
    mongo_manager.close()


# PUBLIC_INTERFACE
def get_mongo_db() -> Optional[AsyncIOMotorDatabase]:
    """Get the MongoDB database handle, or None if MongoDB is not configured."""
    return mongo_manager.get_db()
