"""
MCP (Model Context Protocol) Tools for AI agents.
Implements task CRUD operations with user isolation and validation.
"""
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timezone

from pydantic import BaseModel, Field, ValidationError
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Task

logger = logging.getLogger(__name__)


# ============================================================================
# MCP Tool Parameter Schemas (Pydantic)
# ============================================================================

class AddTaskParams(BaseModel):
    """Parameters for add_task MCP tool."""

    user_id: UUID = Field(..., description="Authenticated user ID (from JWT)")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description (optional)")
    completed: bool = Field(default=False, description="Initial completion status")


class ListTasksParams(BaseModel):
    """Parameters for list_tasks MCP tool."""

    user_id: UUID = Field(..., description="Authenticated user ID (from JWT)")
    completed: Optional[bool] = Field(None, description="Filter by completion status (None = all tasks)")


class UpdateTaskParams(BaseModel):
    """Parameters for update_task MCP tool."""

    user_id: UUID = Field(..., description="Authenticated user ID (from JWT)")
    task_id: UUID = Field(..., description="ID of task to update")
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="New task title")
    description: Optional[str] = Field(None, max_length=1000, description="New task description")


class CompleteTaskParams(BaseModel):
    """Parameters for complete_task MCP tool."""

    user_id: UUID = Field(..., description="Authenticated user ID (from JWT)")
    task_id: UUID = Field(..., description="ID of task to update")
    completed: bool = Field(..., description="New completion status")


class DeleteTaskParams(BaseModel):
    """Parameters for delete_task MCP tool."""

    user_id: UUID = Field(..., description="Authenticated user ID (from JWT)")
    task_id: UUID = Field(..., description="ID of task to delete")


# ============================================================================
# MCP Tool Implementations
# ============================================================================

async def add_task(params: AddTaskParams, session: AsyncSession) -> Dict[str, Any]:
    """
    MCP Tool: Create new task for authenticated user.

    Args:
        params: Validated task creation parameters
        session: Database session

    Returns:
        Dictionary with created task details

    Raises:
        ValidationError: If parameters are invalid
        Exception: If database operation fails
    """
    try:
        # Create new task with user isolation
        task = Task(
            user_id=params.user_id,
            title=params.title,
            description=params.description,
            completed=params.completed,
        )

        session.add(task)
        await session.commit()
        await session.refresh(task)

        logger.info(f"Task created: ID={task.id}, user={params.user_id}, title='{params.title}'")

        return {
            "id": str(task.id),
            "user_id": str(task.user_id),
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }

    except ValidationError as e:
        logger.error(f"Validation error in add_task: {e}")
        raise
    except Exception as e:
        logger.error(f"Database error in add_task: {e}")
        await session.rollback()
        raise


async def list_tasks(params: ListTasksParams, session: AsyncSession) -> List[Dict[str, Any]]:
    """
    MCP Tool: Retrieve tasks for authenticated user with optional status filter.

    Args:
        params: Validated task listing parameters
        session: Database session

    Returns:
        List of task dictionaries

    Raises:
        Exception: If database operation fails
    """
    try:
        # Build query with user isolation
        query = select(Task).where(Task.user_id == params.user_id)

        # Apply completion filter if specified
        if params.completed is not None:
            query = query.where(Task.completed == params.completed)

        # Order by created_at descending (newest first)
        query = query.order_by(Task.created_at.desc())

        result = await session.execute(query)
        tasks = result.scalars().all()

        logger.info(
            f"Tasks retrieved: {len(tasks)} tasks for user={params.user_id}, "
            f"completed_filter={params.completed}"
        )

        return [
            {
                "id": str(task.id),
                "user_id": str(task.user_id),
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            }
            for task in tasks
        ]

    except Exception as e:
        logger.error(f"Database error in list_tasks: {e}")
        raise


async def update_task(params: UpdateTaskParams, session: AsyncSession) -> Dict[str, Any]:
    """
    MCP Tool: Update task title or description for authenticated user.

    Args:
        params: Validated task update parameters
        session: Database session

    Returns:
        Dictionary with updated task details

    Raises:
        ValueError: If task not found or belongs to different user
        Exception: If database operation fails
    """
    try:
        # Fetch task with user isolation
        query = select(Task).where(
            Task.id == params.task_id,
            Task.user_id == params.user_id
        )
        result = await session.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(f"Task not found or access denied: task_id={params.task_id}")

        # Update fields if provided
        if params.title is not None:
            task.title = params.title
        if params.description is not None:
            task.description = params.description

        task.updated_at = datetime.now(timezone.utc)

        await session.commit()
        await session.refresh(task)

        logger.info(f"Task updated: ID={task.id}, user={params.user_id}")

        return {
            "id": str(task.id),
            "user_id": str(task.user_id),
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Database error in update_task: {e}")
        await session.rollback()
        raise


async def complete_task(params: CompleteTaskParams, session: AsyncSession) -> Dict[str, Any]:
    """
    MCP Tool: Mark task as complete or incomplete for authenticated user.

    Args:
        params: Validated task completion parameters
        session: Database session

    Returns:
        Dictionary with updated task details

    Raises:
        ValueError: If task not found or belongs to different user
        Exception: If database operation fails
    """
    try:
        # Fetch task with user isolation
        query = select(Task).where(
            Task.id == params.task_id,
            Task.user_id == params.user_id
        )
        result = await session.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(f"Task not found or access denied: task_id={params.task_id}")

        task.completed = params.completed
        task.updated_at = datetime.now(timezone.utc)

        await session.commit()
        await session.refresh(task)

        logger.info(
            f"Task completion updated: ID={task.id}, user={params.user_id}, "
            f"completed={params.completed}"
        )

        return {
            "id": str(task.id),
            "user_id": str(task.user_id),
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Database error in complete_task: {e}")
        await session.rollback()
        raise


async def delete_task(params: DeleteTaskParams, session: AsyncSession) -> Dict[str, Any]:
    """
    MCP Tool: Permanently delete task for authenticated user.

    Args:
        params: Validated task deletion parameters
        session: Database session

    Returns:
        Dictionary with deletion confirmation

    Raises:
        ValueError: If task not found or belongs to different user
        Exception: If database operation fails
    """
    try:
        # Fetch task with user isolation
        query = select(Task).where(
            Task.id == params.task_id,
            Task.user_id == params.user_id
        )
        result = await session.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(f"Task not found or access denied: task_id={params.task_id}")

        task_id = task.id
        await session.delete(task)
        await session.commit()

        logger.info(f"Task deleted: ID={task_id}, user={params.user_id}")

        return {
            "deleted_task_id": str(task_id),
            "message": f"Task '{task.title}' has been deleted successfully"
        }

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Database error in delete_task: {e}")
        await session.rollback()
        raise
