"""
SQLModel database models for User, Task, Conversation, and Message entities.
Defines table structure, relationships, and validation rules.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlmodel import Column, Field, Relationship, SQLModel
from sqlalchemy import JSON


class User(SQLModel, table=True):
    """User account model."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, max_length=255, index=True)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Relationship to tasks
    tasks: List["Task"] = Relationship(back_populates="owner")


class Task(SQLModel, table=True):
    """Task model with user ownership."""

    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Relationship to owner
    owner: User = Relationship(back_populates="tasks")


class Conversation(SQLModel, table=True):
    """Conversation model for chatbot interactions."""

    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class Message(SQLModel, table=True):
    """Message model for conversation history."""

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True
    )
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True
    )
    role: str = Field(nullable=False)  # 'user' or 'assistant'
    content: str = Field(nullable=False)
    tool_calls: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON)
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
