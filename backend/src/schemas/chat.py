"""
Pydantic schemas for chat API request/response validation.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """Schema for MCP tool execution details."""

    tool: str = Field(..., description="Name of MCP tool executed")
    parameters: Dict[str, Any] = Field(..., description="Input parameters passed to the tool")
    result: Any = Field(..., description="Output returned by the tool")


class ChatRequest(BaseModel):
    """Schema for incoming chat message request."""

    conversation_id: Optional[UUID] = Field(
        None,
        description="UUID of existing conversation (optional for first message)"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's natural language message"
    )


class ChatResponse(BaseModel):
    """Schema for chat message response."""

    conversation_id: UUID = Field(
        ...,
        description="UUID of the conversation (generated for first message)"
    )
    message: str = Field(
        ...,
        description="AI assistant's response message (may include markdown)"
    )
    tool_calls: List[ToolCall] = Field(
        default_factory=list,
        description="List of MCP tool calls executed (empty if no tools called)"
    )
    timestamp: datetime = Field(
        ...,
        description="ISO 8601 timestamp of when response was generated"
    )
