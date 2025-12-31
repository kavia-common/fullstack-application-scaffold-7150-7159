"""Tests for MongoDB integration utilities.

These tests are designed to run without an actual MongoDB instance.
"""

from __future__ import annotations

import pytest

from src.api.db.mongodb import MongoClientManager


class _BoolExplodingDb:
    """A stand-in for a PyMongo/Motor Database object that raises on truthiness.

    PyMongo Database objects raise NotImplementedError on __bool__, which is the
    behavior that caused the production bug.
    """

    def __bool__(self) -> bool:  # pragma: no cover
        raise NotImplementedError("Do not evaluate database objects as booleans")

    async def command(self, _cmd: str) -> dict:
        return {"ok": 1}


@pytest.mark.anyio
async def test_ping_does_not_bool_evaluate_db() -> None:
    """Ensure ping uses explicit None checks and never triggers __bool__."""
    mgr = MongoClientManager()
    # Inject a DB object that raises if `if db:` is used.
    mgr._db = _BoolExplodingDb()  # type: ignore[attr-defined]

    ok = await mgr.ping()
    assert ok is True
