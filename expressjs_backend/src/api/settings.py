"""
Centralized application settings.

This module intentionally uses safe defaults so the service can start cleanly in
local/dev environments without any configuration, while still allowing runtime
configuration via environment variables.

Env vars (all optional):
- API_TITLE: OpenAPI title
- API_DESCRIPTION: OpenAPI description
- API_VERSION: OpenAPI version
- CORS_ALLOW_ORIGINS: Comma-separated list of origins. Use "*" for permissive (default).
- MONGODB_URI: MongoDB connection string (enables Mongo-backed persistence)
- MONGODB_DB: Mongo database name (default "app")
"""

from __future__ import annotations

import os
from typing import List


def _split_csv(value: str) -> List[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


# PUBLIC_INTERFACE
def get_cors_allow_origins() -> List[str]:
    """Return list of CORS allowed origins from env (default: ['*'])."""
    raw = os.getenv("CORS_ALLOW_ORIGINS", "*").strip()
    if raw == "*":
        return ["*"]
    origins = _split_csv(raw)
    return origins or ["*"]


# PUBLIC_INTERFACE
def get_api_metadata() -> dict:
    """Return OpenAPI metadata (title/description/version), with safe defaults."""
    return {
        "title": os.getenv("API_TITLE", "Fullstack Application Scaffold API"),
        "description": os.getenv(
            "API_DESCRIPTION",
            "Production-shaped FastAPI backend for the scaffolded fullstack app. "
            "Includes versioned routing, a sample CRUD resource, and optional MongoDB integration.",
        ),
        "version": os.getenv("API_VERSION", "1.0.0"),
    }
