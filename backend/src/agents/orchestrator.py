"""
Todo-Orchestrator Agent - Main chatbot brain.
Coordinates intent classification, entity extraction, tool selection, and response generation.
"""
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.task_executor import TaskOpsExecutor
from src.services.cohere_service import cohere_service

logger = logging.getLogger(__name__)


class TodoOrchestrator:
    """
    Main orchestrator agent for Todo AI Chatbot.
    Handles natural language understanding and tool orchestration.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize Todo-Orchestrator Agent.

        Args:
            session: Database session for operations
        """
        self.session = session
        self.task_executor = TaskOpsExecutor(session)

    async def process_message(
        self,
        user_id: UUID,
        message: str
    ) -> Dict[str, Any]:
        """
        Process user message and execute appropriate actions.

        Args:
            user_id: User ID from authentication
            message: User's natural language message

        Returns:
            Dictionary with:
            {
                "response_message": str,
                "tool_calls": List[Dict],
                "success": bool
            }
        """
        logger.info(f"Processing message from user {user_id}: '{message[:100]}...'")

        try:
            # Step 1: Classify intent
            intent = cohere_service.classify_intent(message)
            logger.info(f"Classified intent: {intent}")

            if intent == "unknown":
                return {
                    "response_message": (
                        "I'm not sure what you'd like me to do. "
                        "I can help you add, view, update, complete, or delete tasks. "
                        "Try saying something like 'Add a task to buy groceries' or 'Show me my tasks'."
                    ),
                    "tool_calls": [],
                    "success": True
                }

            # Step 2: Extract entities
            entities = cohere_service.extract_entities(message, intent)
            logger.info(f"Extracted entities: {entities}")

            # Step 3: Execute tool based on intent
            if intent == "add":
                return await self._handle_add_task(user_id, entities)
            elif intent == "list":
                return await self._handle_list_tasks(user_id, entities)
            elif intent == "update":
                return await self._handle_update_task(user_id, entities)
            elif intent == "complete":
                return await self._handle_complete_task(user_id, entities)
            elif intent == "delete":
                return await self._handle_delete_task(user_id, entities)
            else:
                return {
                    "response_message": "I encountered an unexpected intent. Please try again.",
                    "tool_calls": [],
                    "success": False
                }

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return {
                "response_message": (
                    "I'm having trouble right now. Please try again in a moment."
                ),
                "tool_calls": [],
                "success": False
            }

    async def _handle_add_task(
        self,
        user_id: UUID,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle 'add' intent - create new task."""
        title = entities.get("title")
        description = entities.get("description")

        if not title:
            return {
                "response_message": (
                    "I'd be happy to add a task! What would you like the task to be? "
                    "For example: 'Add a task to buy groceries'"
                ),
                "tool_calls": [],
                "success": False
            }

        # Execute add_task tool
        result = await self.task_executor.execute_add_task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False
        )

        if result["success"]:
            task_data = result["data"]
            response = f"I've added '{title}' to your task list."
            if description:
                response += f" ({description})"

            return {
                "response_message": response,
                "tool_calls": [{
                    "tool": "add_task",
                    "parameters": {
                        "user_id": str(user_id),
                        "title": title,
                        "description": description,
                        "completed": False
                    },
                    "result": task_data
                }],
                "success": True
            }
        else:
            return {
                "response_message": (
                    f"I couldn't add that task. {result['error']}"
                ),
                "tool_calls": [],
                "success": False
            }

    async def _handle_list_tasks(
        self,
        user_id: UUID,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle 'list' intent - retrieve and display tasks."""
        completed_filter = entities.get("completed")

        # Execute list_tasks tool
        result = await self.task_executor.execute_list_tasks(
            user_id=user_id,
            completed=completed_filter
        )

        if result["success"]:
            tasks = result["data"]

            if not tasks:
                if completed_filter is True:
                    response = "You don't have any completed tasks."
                elif completed_filter is False:
                    response = "You don't have any pending tasks. Great job!"
                else:
                    response = "You don't have any tasks yet. Add one to get started!"

                return {
                    "response_message": response,
                    "tool_calls": [{
                        "tool": "list_tasks",
                        "parameters": {
                            "user_id": str(user_id),
                            "completed": completed_filter
                        },
                        "result": tasks
                    }],
                    "success": True
                }

            # Format tasks for display
            pending_tasks = [t for t in tasks if not t["completed"]]
            completed_tasks = [t for t in tasks if t["completed"]]

            response_parts = ["Here are your tasks:\n"]

            if pending_tasks:
                response_parts.append("\n**Pending:**")
                for i, task in enumerate(pending_tasks, 1):
                    task_id = task["id"]
                    title = task["title"]
                    response_parts.append(f"{i}. Task #{task_id[:8]}: {title}")

            if completed_tasks:
                response_parts.append("\n**Completed:**")
                for i, task in enumerate(completed_tasks, 1):
                    task_id = task["id"]
                    title = task["title"]
                    response_parts.append(f"{i}. Task #{task_id[:8]}: {title}")

            return {
                "response_message": "\n".join(response_parts),
                "tool_calls": [{
                    "tool": "list_tasks",
                    "parameters": {
                        "user_id": str(user_id),
                        "completed": completed_filter
                    },
                    "result": tasks
                }],
                "success": True
            }
        else:
            return {
                "response_message": (
                    f"I couldn't retrieve your tasks. {result['error']}"
                ),
                "tool_calls": [],
                "success": False
            }

    async def _handle_update_task(
        self,
        user_id: UUID,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle 'update' intent - modify task title/description."""
        task_id = entities.get("task_id")
        title = entities.get("title")
        description = entities.get("description")

        if not task_id:
            return {
                "response_message": (
                    "Which task would you like to update? "
                    "Please provide the task ID or use 'Show me my tasks' first."
                ),
                "tool_calls": [],
                "success": False
            }

        if not title and not description:
            return {
                "response_message": (
                    "What would you like to update? "
                    "Please provide a new title or description."
                ),
                "tool_calls": [],
                "success": False
            }

        # Convert task_id to UUID
        try:
            task_uuid = UUID(str(task_id)) if not isinstance(task_id, UUID) else task_id
        except (ValueError, AttributeError):
            return {
                "response_message": "Invalid task ID format. Please check the task ID.",
                "tool_calls": [],
                "success": False
            }

        # Execute update_task tool
        result = await self.task_executor.execute_update_task(
            user_id=user_id,
            task_id=task_uuid,
            title=title,
            description=description
        )

        if result["success"]:
            task_data = result["data"]
            response = f"I've updated task #{str(task_uuid)[:8]}."

            return {
                "response_message": response,
                "tool_calls": [{
                    "tool": "update_task",
                    "parameters": {
                        "user_id": str(user_id),
                        "task_id": str(task_uuid),
                        "title": title,
                        "description": description
                    },
                    "result": task_data
                }],
                "success": True
            }
        else:
            return {
                "response_message": (
                    f"I couldn't update that task. {result['error']}"
                ),
                "tool_calls": [],
                "success": False
            }

    async def _handle_complete_task(
        self,
        user_id: UUID,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle 'complete' intent - mark task as done/undone."""
        task_id = entities.get("task_id")
        completed = entities.get("completed", True)  # Default to marking as complete

        if not task_id:
            return {
                "response_message": (
                    "Which task would you like to complete? "
                    "Please provide the task ID or use 'Show me my tasks' first."
                ),
                "tool_calls": [],
                "success": False
            }

        # Convert task_id to UUID
        try:
            task_uuid = UUID(str(task_id)) if not isinstance(task_id, UUID) else task_id
        except (ValueError, AttributeError):
            return {
                "response_message": "Invalid task ID format. Please check the task ID.",
                "tool_calls": [],
                "success": False
            }

        # Execute complete_task tool
        result = await self.task_executor.execute_complete_task(
            user_id=user_id,
            task_id=task_uuid,
            completed=completed
        )

        if result["success"]:
            task_data = result["data"]
            status_word = "completed" if completed else "reopened"
            response = f"I've marked task #{str(task_uuid)[:8]} as {status_word}."

            return {
                "response_message": response,
                "tool_calls": [{
                    "tool": "complete_task",
                    "parameters": {
                        "user_id": str(user_id),
                        "task_id": str(task_uuid),
                        "completed": completed
                    },
                    "result": task_data
                }],
                "success": True
            }
        else:
            return {
                "response_message": (
                    f"I couldn't update that task's status. {result['error']}"
                ),
                "tool_calls": [],
                "success": False
            }

    async def _handle_delete_task(
        self,
        user_id: UUID,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle 'delete' intent - remove task."""
        task_id = entities.get("task_id")

        if not task_id:
            return {
                "response_message": (
                    "Which task would you like to delete? "
                    "Please provide the task ID or use 'Show me my tasks' first."
                ),
                "tool_calls": [],
                "success": False
            }

        # Convert task_id to UUID
        try:
            task_uuid = UUID(str(task_id)) if not isinstance(task_id, UUID) else task_id
        except (ValueError, AttributeError):
            return {
                "response_message": "Invalid task ID format. Please check the task ID.",
                "tool_calls": [],
                "success": False
            }

        # Execute delete_task tool
        result = await self.task_executor.execute_delete_task(
            user_id=user_id,
            task_id=task_uuid
        )

        if result["success"]:
            deletion_data = result["data"]
            response = deletion_data["message"]

            return {
                "response_message": response,
                "tool_calls": [{
                    "tool": "delete_task",
                    "parameters": {
                        "user_id": str(user_id),
                        "task_id": str(task_uuid)
                    },
                    "result": deletion_data
                }],
                "success": True
            }
        else:
            return {
                "response_message": (
                    f"I couldn't delete that task. {result['error']}"
                ),
                "tool_calls": [],
                "success": False
            }
