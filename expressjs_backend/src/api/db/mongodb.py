"""
MongoDB integration layer.

This module is intentionally resilient:
- If MONGODB_URI is not provided, the API still runs and falls back to in-memory storage.
- If MongoDB is unreachable, endpoints that require the DB can gracefully fallback (where designed).

Env vars (optional):
- MONGODB_URI: MongoDB connection string, e.g. mongodb://localhost:27017
- MONGODB_DB: Database name (default: "app")
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
        self._client = AsyncIOMotorClient(mongodb_uri)
        self._db = self._client[db_name]

    async def ping(self) -> bool:
        """Return True if MongoDB is configured and reachable, else False."""
        if not self._db:
            return False
        try:
            await self._db.command("ping")
            return True
        except Exception:
            return False

    def get_db(self) -> Optional[AsyncIOMotorDatabase]:
        """Return the configured database handle (or None if not configured)."""
        return self._db

    def close(self) -> None:
        """Close the Mongo client if open."""
        if self._client is not None:
            self._client.close()
        self._client = None
        self._db = None


mongo_manager = MongoClientManager()


# PUBLIC_INTERFACE
async def init_mongo() -> None:
    """Initialize MongoDB connection manager from environment variables."""
    mongo_manager.configure_from_env()


# PUBLIC_INTERFACE
async def close_mongo() -> None:
    """Close MongoDB resources, if any."""
    mongo_manager.close()


# PUBLIC_INTERFACE
def get_mongo_db() -> Optional[AsyncIOMotorDatabase]:
    """Get the MongoDB database handle, or None if MongoDB is not configured."""
    return mongo_manager.get_db()
