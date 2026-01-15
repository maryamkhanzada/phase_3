"""
Conversation-Memory Agent for managing chatbot conversation state.
Handles conversation persistence, message storage, and history retrieval.
"""
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Conversation, Message

logger = logging.getLogger(__name__)


class ConversationMemoryAgent:
    """
    Agent for managing conversation state in a stateless architecture.
    All conversation data is persisted in PostgreSQL/SQLite database.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize Conversation-Memory Agent.

        Args:
            session: Database session for persistence operations
        """
        self.session = session

    async def create_conversation(self, user_id: UUID) -> Conversation:
        """
        Create a new conversation for the user.

        Args:
            user_id: User ID who owns the conversation

        Returns:
            Created Conversation object

        Raises:
            Exception: If database operation fails
        """
        try:
            conversation = Conversation(
                id=uuid4(),
                user_id=user_id,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )

            self.session.add(conversation)
            await self.session.commit()
            await self.session.refresh(conversation)

            logger.info(f"Conversation created: ID={conversation.id}, user={user_id}")

            return conversation

        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            await self.session.rollback()
            raise

    async def get_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID
    ) -> Optional[Conversation]:
        """
        Retrieve conversation by ID with user isolation.

        Args:
            conversation_id: UUID of conversation
            user_id: User ID for ownership verification

        Returns:
            Conversation object or None if not found/access denied

        Raises:
            Exception: If database operation fails
        """
        try:
            query = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            result = await self.session.execute(query)
            conversation = result.scalar_one_or_none()

            if conversation:
                logger.info(f"Conversation retrieved: ID={conversation_id}, user={user_id}")
            else:
                logger.warning(
                    f"Conversation not found or access denied: "
                    f"ID={conversation_id}, user={user_id}"
                )

            return conversation

        except Exception as e:
            logger.error(f"Failed to retrieve conversation: {e}")
            raise

    async def save_message(
        self,
        conversation_id: UUID,
        user_id: UUID,
        role: str,
        content: str,
        tool_calls: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        Save a message to the conversation.

        Args:
            conversation_id: UUID of conversation
            user_id: User ID who owns the conversation
            role: Message role ('user' or 'assistant')
            content: Message text content
            tool_calls: Optional dictionary of tool call details

        Returns:
            Created Message object

        Raises:
            ValueError: If role is invalid
            Exception: If database operation fails
        """
        if role not in ('user', 'assistant'):
            raise ValueError(f"Invalid role: {role}. Must be 'user' or 'assistant'")

        try:
            message = Message(
                conversation_id=conversation_id,
                user_id=user_id,
                role=role,
                content=content,
                tool_calls=tool_calls,
                created_at=datetime.now(timezone.utc)
            )

            self.session.add(message)

            # Update conversation updated_at timestamp
            query = select(Conversation).where(Conversation.id == conversation_id)
            result = await self.session.execute(query)
            conversation = result.scalar_one_or_none()

            if conversation:
                conversation.updated_at = datetime.now(timezone.utc)

            await self.session.commit()
            await self.session.refresh(message)

            logger.info(
                f"Message saved: conversation={conversation_id}, role={role}, "
                f"has_tool_calls={tool_calls is not None}"
            )

            return message

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            await self.session.rollback()
            raise

    async def get_conversation_history(
        self,
        conversation_id: UUID,
        user_id: UUID,
        limit: int = 20
    ) -> List[Message]:
        """
        Retrieve conversation history (last N messages).

        Args:
            conversation_id: UUID of conversation
            user_id: User ID for ownership verification
            limit: Maximum number of messages to retrieve (default: 20)

        Returns:
            List of Message objects ordered by created_at ascending (oldest first)

        Raises:
            Exception: If database operation fails
        """
        try:
            # Verify conversation belongs to user
            conversation = await self.get_conversation(conversation_id, user_id)
            if not conversation:
                logger.warning(
                    f"Cannot retrieve history - conversation not found: "
                    f"ID={conversation_id}, user={user_id}"
                )
                return []

            # Fetch last N messages, ordered by created_at descending, then reverse
            query = (
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.desc())
                .limit(limit)
            )

            result = await self.session.execute(query)
            messages = result.scalars().all()

            # Reverse to get chronological order (oldest first)
            messages_list = list(reversed(messages))

            logger.info(
                f"Conversation history retrieved: {len(messages_list)} messages "
                f"for conversation={conversation_id}"
            )

            return messages_list

        except Exception as e:
            logger.error(f"Failed to retrieve conversation history: {e}")
            raise

    async def format_history_for_context(
        self,
        conversation_id: UUID,
        user_id: UUID,
        limit: int = 20
    ) -> List[Dict[str, str]]:
        """
        Format conversation history for AI model context.

        Args:
            conversation_id: UUID of conversation
            user_id: User ID for ownership verification
            limit: Maximum number of messages to retrieve (default: 20)

        Returns:
            List of message dictionaries with 'role' and 'content' keys

        Raises:
            Exception: If database operation fails
        """
        try:
            messages = await self.get_conversation_history(
                conversation_id,
                user_id,
                limit
            )

            formatted_messages = [
                {
                    "role": msg.role,
                    "content": msg.content
                }
                for msg in messages
            ]

            return formatted_messages

        except Exception as e:
            logger.error(f"Failed to format history for context: {e}")
            raise
