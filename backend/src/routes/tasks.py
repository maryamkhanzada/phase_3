"""
Task CRUD endpoints.
Provides REST API for task management with user isolation.
"""
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt import get_current_user
from src.db import get_session
from src.exceptions import BadRequestException, NotFoundException
from src.models import Task
from src.schemas.task import TaskCreateRequest, TaskListResponse, TaskResponse, TaskUpdateRequest

router = APIRouter(prefix="/api", tags=["Tasks"])


@router.get("/tasks", response_model=TaskListResponse)
async def get_tasks(
    current_user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Fetch all tasks for authenticated user.

    Args:
        current_user_id: User ID from JWT token
        session: Database session

    Returns:
        TaskListResponse with list of user's tasks

    Raises:
        401: Unauthorized (missing or invalid token)
    """
    # Query tasks filtered by user_id (CRITICAL: enforces user isolation)
    result = await session.execute(
        select(Task)
        .where(Task.user_id == UUID(current_user_id))
        .order_by(Task.created_at.desc())
    )
    tasks = result.scalars().all()

    return TaskListResponse(tasks=[TaskResponse.model_validate(task) for task in tasks])


@router.post("/tasks", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_task(
    request: TaskCreateRequest,
    current_user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new task for authenticated user.

    Args:
        request: Task creation request with title and optional description
        current_user_id: User ID from JWT token (automatically set, NEVER from request body)
        session: Database session

    Returns:
        Created task wrapped in {"task": TaskResponse}

    Raises:
        400: Invalid title (empty or too long)
        401: Unauthorized (missing or invalid token)
    """
    # Validate title is not empty after trimming
    if not request.title.strip():
        raise BadRequestException(detail="Title cannot be empty")

    # Create new task
    # CRITICAL: user_id from JWT token, NEVER from client request
    new_task = Task(
        title=request.title.strip(),
        description=request.description.strip() if request.description else None,
        completed=False,
        user_id=UUID(current_user_id),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    return {"task": TaskResponse.model_validate(new_task)}


@router.put("/tasks/{task_id}", response_model=dict)
async def update_task(
    task_id: UUID,
    request: TaskUpdateRequest,
    current_user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing task (partial update supported).

    Args:
        task_id: Task UUID to update
        request: Task update request with optional fields
        current_user_id: User ID from JWT token
        session: Database session

    Returns:
        Updated task wrapped in {"task": TaskResponse}

    Raises:
        400: Invalid input (e.g., empty title)
        401: Unauthorized (missing or invalid token)
        404: Task not found or not owned by user
    """
    # Query task with ownership verification
    # CRITICAL: Combined existence + ownership check (prevents cross-user access)
    result = await session.execute(
        select(Task)
        .where(Task.id == task_id)
        .where(Task.user_id == UUID(current_user_id))
    )
    task = result.scalar_one_or_none()

    if not task:
        # Return 404 for both "doesn't exist" and "not owned" (security: no information leakage)
        raise NotFoundException(detail="Task not found")

    # Validate and apply updates (partial update support)
    if request.title is not None:
        if not request.title.strip():
            raise BadRequestException(detail="Title cannot be empty")
        task.title = request.title.strip()

    if request.description is not None:
        task.description = request.description.strip() if request.description else None

    if request.completed is not None:
        task.completed = request.completed

    # Update timestamp
    task.updated_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(task)

    return {"task": TaskResponse.model_validate(task)}


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a task permanently.

    Args:
        task_id: Task UUID to delete
        current_user_id: User ID from JWT token
        session: Database session

    Returns:
        204 No Content (empty response body)

    Raises:
        401: Unauthorized (missing or invalid token)
        404: Task not found or not owned by user
    """
    # Query task with ownership verification
    # CRITICAL: Combined existence + ownership check
    result = await session.execute(
        select(Task)
        .where(Task.id == task_id)
        .where(Task.user_id == UUID(current_user_id))
    )
    task = result.scalar_one_or_none()

    if not task:
        # Return 404 for both "doesn't exist" and "not owned"
        raise NotFoundException(detail="Task not found")

    # Delete task
    await session.delete(task)
    await session.commit()

    # Return 204 No Content (empty response)
    return None
