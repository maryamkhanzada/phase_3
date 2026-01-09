"""
Task request and response schemas.
Defines Pydantic models for task CRUD operations.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TaskCreateRequest(BaseModel):
    """Task creation request payload."""

    title: str = Field(..., min_length=1, max_length=255, description="Task title (required, max 255 chars)")
    description: Optional[str] = Field(None, max_length=1000, description="Task description (optional, max 1000 chars)")


class TaskUpdateRequest(BaseModel):
    """Task update request payload (all fields optional for partial updates)."""

    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    completed: Optional[bool] = Field(None, description="Task completion status")


class TaskResponse(BaseModel):
    """Task data in responses."""

    id: UUID = Field(..., description="Task UUID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    completed: bool = Field(..., description="Task completion status")
    user_id: UUID = Field(..., description="Owner user UUID")
    created_at: datetime = Field(..., description="Creation timestamp (ISO 8601 UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (ISO 8601 UTC)")

    class Config:
        from_attributes = True  # Enable ORM mode for SQLModel compatibility


class TaskListResponse(BaseModel):
    """Response for GET /api/tasks endpoint."""

    tasks: List[TaskResponse] = Field(..., description="List of tasks")
