"""
Task-Ops-Executor Agent for executing task operations via MCP tools.
Wraps MCP tool calls with error handling and result formatting.
"""
import logging
from typing import Dict, Any, List
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents import mcp_tools
from src.agents.mcp_tools import (
    AddTaskParams,
    ListTasksParams,
    UpdateTaskParams,
    CompleteTaskParams,
    DeleteTaskParams
)

logger = logging.getLogger(__name__)


class TaskOpsExecutor:
    """
    Agent for executing task operations using MCP tools.
    Provides error handling and result formatting for orchestrator.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize Task-Ops-Executor Agent.

        Args:
            session: Database session for MCP tool operations
        """
        self.session = session

    async def execute_add_task(
        self,
        user_id: UUID,
        title: str,
        description: str = None,
        completed: bool = False
    ) -> Dict[str, Any]:
        """
        Execute add_task MCP tool.

        Args:
            user_id: User ID from authentication
            title: Task title
            description: Task description (optional)
            completed: Initial completion status

        Returns:
            Dictionary with tool execution result:
            {
                "success": bool,
                "data": dict or None,
                "error": str or None
            }
        """
        try:
            params = AddTaskParams(
                user_id=user_id,
                title=title,
                description=description,
                completed=completed
            )

            result = await mcp_tools.add_task(params, self.session)

            logger.info(f"add_task executed successfully: task_id={result['id']}")

            return {
                "success": True,
                "data": result,
                "error": None
            }

        except ValidationError as e:
            error_msg = f"Validation error: {e}"
            logger.error(f"add_task validation failed: {error_msg}")
            return {
                "success": False,
                "data": None,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Failed to create task: {str(e)}"
            logger.error(f"add_task execution failed: {error_msg}")
            return {
                "success": False,
                "data": None,
                "error": error_msg
            }

    async def execute_list_tasks(
        self,
        user_id: UUID,
        completed: bool = None
    ) -> Dict[str, Any]:
        """
        Execute list_tasks MCP tool.

        Args:
            user_id: User ID from authentication
            completed: Filter by completion status (None = all tasks)

        Returns:
            Dictionary with tool execution result
        """
        try:
            params = ListTasksParams(
                user_id=user_id,
                completed=completed
            )

            result = await mcp_tools.list_tasks(params, self.session)

            logger.info(f"list_tasks executed successfully: {len(result)} tasks retrieved")

            return {
                "success": True,
                "data": result,
                "error": None
            }

        except Exception as e:
            error_msg = f"Failed to retrieve tasks: {str(e)}"
            logger.error(f"list_tasks execution failed: {error_msg}")
            return {
                "success": False,
                "data": None,
                "error": error_msg
            }

    async def execute_update_task(
        self,
        user_id: UUID,
        task_id: UUID,
        title: str = None,
        description: str = None
    ) -> Dict[str, Any]:
        """
        Execute update_task MCP tool.

        Args:
            user_id: User ID from authentication
            task_id: ID of task to update
            title: New task title (optional)
            description: New task description (optional)

        Returns:
            Dictionary with tool execution result
        """
        try:
            params = UpdateTaskParams(
                user_id=user_id,
                task_id=task_id,
                title=title,
                description=description
            )

            result = await mcp_tools.update_task(params, self.session)

            logger.info(f"update_task executed successfully: task_id={result['id']}")

            return {
                "success": True,
                "data": result,
                "error": None
            }

        except ValueError as e:
            error_msg = f"Task not found or access denied: {str(e)}"
            logger.error(f"update_task failed: {error_msg}")
            return {
                "success": False,
                "data": None,
                "error": error_msg
            }
        except ValidationError as e:
            error_msg = f"Validation error: {e}"
            logger.error(f"update_task validation failed: {error_msg}")
            return {
                "success": False,
                "data": None,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Failed to update task: {str(e)}"
            logger.error(f"update_task execution failed: {error_msg}")
            return {
                "success": False,
                "data": None,
                "error": error_msg
            }

    async def execute_complete_task(
        self,
        user_id: UUID,
        task_id: UUID,
        completed: bool
    ) -> Dict[str, Any]:
        """
        Execute complete_task MCP tool.

        Args:
            user_id: User ID from authentication
            task_id: ID of task to update
            completed: New completion status

        Returns:
            Dictionary with tool execution result
        """
        try:
            params = CompleteTaskParams(
                user_id=user_id,
                task_id=task_id,
                completed=completed
            )

            result = await mcp_tools.complete_task(params, self.session)

            logger.info(
                f"complete_task executed successfully: task_id={result['id']}, "
                f"completed={completed}"
            )

            return {
                "success": True,
                "data": result,
                "error": None
            }

        except ValueError as e:
            error_msg = f"Task not found or access denied: {str(e)}"
            logger.error(f"complete_task failed: {error_msg}")
            return {
                "success": False,
                "data": None,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Failed to update task completion: {str(e)}"
            logger.error(f"complete_task execution failed: {error_msg}")
            return {
                "success": False,
                "data": None,
                "error": error_msg
            }

    async def execute_delete_task(
        self,
        user_id: UUID,
        task_id: UUID
    ) -> Dict[str, Any]:
        """
        Execute delete_task MCP tool.

        Args:
            user_id: User ID from authentication
            task_id: ID of task to delete

        Returns:
            Dictionary with tool execution result
        """
        try:
            params = DeleteTaskParams(
                user_id=user_id,
                task_id=task_id
            )

            result = await mcp_tools.delete_task(params, self.session)

            logger.info(f"delete_task executed successfully: task_id={task_id}")

            return {
                "success": True,
                "data": result,
                "error": None
            }

        except ValueError as e:
            error_msg = f"Task not found or access denied: {str(e)}"
            logger.error(f"delete_task failed: {error_msg}")
            return {
                "success": False,
                "data": None,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Failed to delete task: {str(e)}"
            logger.error(f"delete_task execution failed: {error_msg}")
            return {
                "success": False,
                "data": None,
                "error": error_msg
            }
