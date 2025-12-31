"""Pydantic models for the Tasks resource."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """Common fields shared by create/update/read task payloads."""

    title: str = Field(..., min_length=1, max_length=200, description="Short task title")
    description: Optional[str] = Field(
        default=None, max_length=4000, description="Optional longer description"
    )
    completed: bool = Field(default=False, description="Whether the task is completed")


class TaskCreate(TaskBase):
    """Payload to create a task."""


class TaskUpdate(BaseModel):
    """Payload to partially update a task."""

    title: Optional[str] = Field(
        default=None, min_length=1, max_length=200, description="Short task title"
    )
    description: Optional[str] = Field(
        default=None, max_length=4000, description="Optional longer description"
    )
    completed: Optional[bool] = Field(default=None, description="Whether the task is completed")


class TaskOut(TaskBase):
    """Task representation returned by the API."""

    id: str = Field(..., description="Task identifier")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")
