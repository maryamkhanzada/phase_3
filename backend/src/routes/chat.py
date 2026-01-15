"""
Chat API routes for AI Todo Chatbot.
Handles natural language task management through conversational interface.
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt import get_current_user_id
from src.db import get_session
from src.schemas.chat import ChatRequest, ChatResponse, ToolCall
from src.agents.conversation_memory import ConversationMemoryAgent
from src.agents.orchestrator import TodoOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def send_chat_message(
    user_id: str,
    request: ChatRequest,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Process a natural language message from the user and execute task operations.

    **Authentication**: Requires valid JWT token in Authorization header.

    **User Isolation**: User ID in path must match authenticated user from JWT.

    **Flow**:
    1. Verify user_id matches JWT
    2. Get or create conversation
    3. Save user message to database
    4. Process message with Todo-Orchestrator Agent
    5. Save assistant response to database
    6. Return response with tool calls

    Args:
        user_id: User ID from URL path (must match JWT)
        request: ChatRequest with message and optional conversation_id
        current_user_id: User ID from JWT authentication (injected)
        session: Database session (injected)

    Returns:
        ChatResponse with assistant message, tool calls, and conversation ID

    Raises:
        HTTPException 400: Invalid request (missing message, etc.)
        HTTPException 401: Authentication failed
        HTTPException 403: User ID doesn't match JWT
        HTTPException 500: Internal server error
    """
    try:
        # Convert user_id from path to UUID
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )

        # Verify user_id matches JWT
        if user_uuid != current_user_id:
            logger.warning(
                f"User ID mismatch: path={user_uuid}, jwt={current_user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this conversation."
            )

        # Validate message
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty."
            )

        # Initialize agents
        memory_agent = ConversationMemoryAgent(session)
        orchestrator = TodoOrchestrator(session)

        # Get or create conversation
        conversation = None
        if request.conversation_id:
            # Existing conversation
            conversation = await memory_agent.get_conversation(
                request.conversation_id,
                user_uuid
            )
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to access this conversation."
                )
        else:
            # New conversation
            conversation = await memory_agent.create_conversation(user_uuid)

        logger.info(
            f"Processing chat message: user={user_uuid}, "
            f"conversation={conversation.id}, message_length={len(request.message)}"
        )

        # Save user message
        await memory_agent.save_message(
            conversation_id=conversation.id,
            user_id=user_uuid,
            role="user",
            content=request.message,
            tool_calls=None
        )

        # Process message with orchestrator
        orchestrator_result = await orchestrator.process_message(
            user_id=user_uuid,
            message=request.message
        )

        assistant_message = orchestrator_result["response_message"]
        tool_calls_data = orchestrator_result.get("tool_calls", [])

        # Save assistant message
        await memory_agent.save_message(
            conversation_id=conversation.id,
            user_id=user_uuid,
            role="assistant",
            content=assistant_message,
            tool_calls={"tool_calls": tool_calls_data} if tool_calls_data else None
        )

        # Format tool calls for response
        tool_calls = [
            ToolCall(
                tool=tc["tool"],
                parameters=tc["parameters"],
                result=tc["result"]
            )
            for tc in tool_calls_data
        ]

        # Create response
        response = ChatResponse(
            conversation_id=conversation.id,
            message=assistant_message,
            tool_calls=tool_calls,
            timestamp=datetime.now(timezone.utc)
        )

        logger.info(
            f"Chat message processed successfully: conversation={conversation.id}, "
            f"tool_calls={len(tool_calls)}"
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        logger.error(f"Unexpected error in send_chat_message: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="I'm having trouble right now. Please try again in a moment."
        )
