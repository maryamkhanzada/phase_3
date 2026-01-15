# Research Document: AI Todo Chatbot Integration

**Feature**: AI Todo Chatbot Integration
**Branch**: `001-ai-chatbot-integration`
**Date**: 2026-01-14
**Phase**: Phase 0 - Research & Technology Decisions

## Purpose

This document captures research findings, technology decisions, and best practices for implementing the AI Todo Chatbot integration. All decisions documented here resolve NEEDS CLARIFICATION items from the Technical Context and establish patterns for Phase 1 design.

---

## 1. Cohere API Integration for NLP

### Decision: Use Cohere Command Model for Intent Classification and Entity Extraction

**Rationale**:
- **Command Model**: Cohere's latest model optimized for instruction-following and structured output
- **Intent Classification**: Use `co.classify()` with custom intents (add, list, update, complete, delete)
- **Entity Extraction**: Use `co.generate()` with structured prompts or `co.chat()` for conversational extraction
- **Embedding Generation**: Use `co.embed()` for future semantic search capabilities

**Alternatives Considered**:
1. **Cohere Classify API Only**: Limited to predefined intent classes, less flexible for entity extraction
   - **Rejected**: Need entity extraction (task_id, title, description) beyond simple classification
2. **Cohere Chat API for Everything**: More conversational but higher token usage
   - **Partially Adopted**: Use for complex multi-step commands (P5 user story)
3. **Custom Fine-Tuned Model**: Better accuracy but requires training data and maintenance
   - **Rejected**: Out of scope for Phase III, pre-trained models sufficient for standard task commands

**Implementation Pattern**:

```python
# Intent Classification
import cohere

co = cohere.Client(api_key=settings.COHERE_API_KEY)

def classify_intent(message: str) -> str:
    """
    Classify user message into task management intents.
    Returns: "add", "list", "update", "complete", "delete", or "unknown"
    """
    response = co.classify(
        model='embed-english-v3.0',
        inputs=[message],
        examples=[
            ("Add a task to buy milk", "add"),
            ("Create a reminder for dentist appointment", "add"),
            ("Show me my tasks", "list"),
            ("What do I need to do?", "list"),
            ("Mark task 5 as done", "complete"),
            ("Complete buy groceries", "complete"),
            ("Update task 3 title to review code", "update"),
            ("Change description of task 7", "update"),
            ("Delete task 12", "delete"),
            ("Remove the completed tasks", "delete"),
        ]
    )
    return response.classifications[0].prediction

# Entity Extraction
def extract_entities(message: str, intent: str) -> dict:
    """
    Extract task entities from message based on detected intent.
    Returns: dict with task_id, title, description, status, etc.
    """
    prompt = f"""
    Extract task information from the following user message.
    Intent: {intent}
    Message: "{message}"

    Return a JSON object with these fields (use null if not mentioned):
    - task_id: integer task ID if mentioned
    - title: string task title
    - description: string task description
    - completed: boolean completion status

    JSON:
    """

    response = co.generate(
        model='command',
        prompt=prompt,
        temperature=0.1,  # Low temperature for deterministic extraction
        max_tokens=200
    )

    # Parse JSON from response
    import json
    return json.loads(response.generations[0].text.strip())
```

**Best Practices**:
- **Temperature**: Use low temperature (0.1-0.2) for intent classification and entity extraction to ensure deterministic results
- **Few-Shot Examples**: Provide 8-10 examples per intent class for accurate classification
- **Error Handling**: Wrap Cohere API calls in try-except to handle rate limits, network errors, and invalid responses
- **Caching**: Cache intent classification results for identical messages within conversation (optimization for future)
- **Token Management**: Limit conversation history to last 20 messages (≈2000 tokens) to stay within Cohere limits

---

## 2. OpenAI Agents SDK with Cohere Integration

### Decision: Use OpenAI Agents SDK with Custom Cohere Model Provider

**Rationale**:
- **Agent Orchestration**: Agents SDK provides robust framework for multi-agent handoffs and tool management
- **Custom Model Provider**: Replace default Gemini/OpenAI provider with Cohere client
- **Tool Integration**: SDK handles MCP tool schema validation and execution automatically
- **Conversation Management**: Built-in context handling and message threading

**Alternatives Considered**:
1. **LangChain with Cohere**: Popular framework but heavier dependencies and more complex for simple use case
   - **Rejected**: Overkill for our three-agent architecture, prefer lighter solution
2. **Custom Agent Implementation**: Full control but requires building orchestration logic from scratch
   - **Rejected**: Reinventing the wheel, Agents SDK provides proven patterns
3. **OpenAI Agents SDK with OpenAI Models**: Simpler integration but violates constitution (must use Cohere)
   - **Rejected**: Constitution mandates Cohere API for NLP tasks

**Implementation Pattern**:

```python
# Custom Cohere Model Provider for Agents SDK
from agents import Agent, ModelProvider
import cohere

class CohereModelProvider(ModelProvider):
    """Custom model provider that uses Cohere API instead of OpenAI/Gemini"""

    def __init__(self, api_key: str, model_name: str = "command"):
        self.client = cohere.Client(api_key)
        self.model_name = model_name

    def generate(self, messages: list, tools: list = None, **kwargs):
        """
        Generate response using Cohere Chat API.
        Converts Agents SDK message format to Cohere format.
        """
        # Convert messages to Cohere chat format
        chat_history = self._convert_messages(messages)

        # Convert tools to Cohere tools format if provided
        cohere_tools = self._convert_tools(tools) if tools else None

        response = self.client.chat(
            model=self.model_name,
            message=messages[-1].content,
            chat_history=chat_history[:-1],
            tools=cohere_tools,
            temperature=0.3
        )

        return self._convert_response(response)

    def _convert_messages(self, messages):
        """Convert SDK message format to Cohere format"""
        return [
            {"role": msg.role, "message": msg.content}
            for msg in messages
        ]

    def _convert_tools(self, tools):
        """Convert SDK tool schemas to Cohere tool format"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameter_definitions": tool.parameters
            }
            for tool in tools
        ]

    def _convert_response(self, response):
        """Convert Cohere response to SDK format"""
        # Implementation details...
        pass

# Agent Initialization
from agents import Agent, handoff

# Create model provider
model_provider = CohereModelProvider(api_key=settings.COHERE_API_KEY)

# Define agents
task_executor = Agent(
    name="Task Operations Agent",
    model=model_provider,
    tools=[add_task, list_tasks, update_task, complete_task, delete_task]
)

conversation_memory = Agent(
    name="Conversation Memory Agent",
    model=model_provider,
    tools=[save_message, get_conversation_history]
)

orchestrator = Agent(
    name="Todo Orchestrator Agent",
    model=model_provider,
    handoffs=[task_executor, handoff(conversation_memory)],
    system_prompt="""
    You are a helpful AI assistant for managing todo tasks.
    Understand user intent, extract task details, and use the appropriate tools.
    Be friendly, conversational, and provide clear confirmations.
    """
)
```

**Best Practices**:
- **System Prompts**: Define clear, specific system prompts for each agent's role
- **Tool Schemas**: Use Pydantic models for tool parameter validation
- **Handoff Logic**: Use explicit handoff conditions to prevent infinite loops between agents
- **Error Recovery**: Implement retry logic with exponential backoff for transient failures
- **Logging**: Log all agent decisions, tool calls, and handoffs for debugging

---

## 3. MCP Tool Implementation Best Practices

### Decision: Implement MCP Tools as Standalone Functions with Pydantic Validation

**Rationale**:
- **Type Safety**: Pydantic models provide runtime validation and type hints
- **Reusability**: Standalone functions can be called directly or via Agents SDK
- **Testing**: Easier to unit test individual functions
- **Schema Generation**: Pydantic models auto-generate JSON schema for tool definitions

**Alternatives Considered**:
1. **Class-Based Tools**: More object-oriented but adds unnecessary complexity
   - **Rejected**: Functions are sufficient for stateless tools
2. **Raw Dict Parameters**: Simpler but no validation or type safety
   - **Rejected**: Risk of runtime errors from invalid parameters
3. **SQLAlchemy ORM**: More powerful but heavier than SQLModel
   - **Rejected**: Constitution mandates SQLModel

**Implementation Pattern**:

```python
# MCP Tool Definitions with Pydantic
from pydantic import BaseModel, Field, validator
from typing import Optional
from sqlmodel import Session, select
from backend.src.models import Task
from backend.src.db import get_session

class AddTaskParams(BaseModel):
    """Parameters for add_task MCP tool"""
    user_id: str = Field(..., description="Authenticated user ID from JWT")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    completed: bool = Field(False, description="Task completion status")

    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Task title cannot be empty")
        return v.strip()

class AddTaskResult(BaseModel):
    """Result from add_task MCP tool"""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: str
    updated_at: str

def add_task(params: AddTaskParams) -> AddTaskResult:
    """
    MCP Tool: Create a new task for the authenticated user.

    Args:
        params: Validated AddTaskParams object

    Returns:
        AddTaskResult with created task details

    Raises:
        PermissionError: If user_id is invalid
        ValueError: If validation fails
    """
    with get_session() as session:
        # Create new task
        task = Task(
            user_id=params.user_id,
            title=params.title,
            description=params.description,
            completed=params.completed
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        return AddTaskResult(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat()
        )

# Tool Registration with Agents SDK
from agents import Tool

add_task_tool = Tool(
    name="add_task",
    description="Create a new task for the user",
    function=lambda params: add_task(AddTaskParams(**params)),
    parameters=AddTaskParams.schema()
)
```

**Best Practices**:
- **User Isolation**: Always filter by `user_id` in WHERE clauses, never trust IDs from request
- **Input Validation**: Use Pydantic validators for business logic constraints
- **Error Handling**: Raise specific exceptions (PermissionError, NotFoundError, ValidationError) for different failure modes
- **Logging**: Log tool invocation with user_id, parameters, and result for audit trail
- **Transaction Management**: Use database transactions to ensure atomicity of multi-step operations
- **Testing**: Write unit tests for each tool with mocked database sessions

---

## 4. Stateless Conversation Management

### Decision: Retrieve Conversation History from Database on Every Request

**Rationale**:
- **Horizontal Scaling**: Stateless servers can be added/removed without losing conversation state
- **Fault Tolerance**: Server restarts don't lose conversations
- **Audit Trail**: All messages persisted for debugging and compliance
- **Multi-Device Support**: Users can continue conversations across devices

**Alternatives Considered**:
1. **In-Memory Session Store (Redis)**: Faster but adds dependency and single point of failure
   - **Rejected**: Constitution mandates stateless backend architecture
2. **Client-Side State Only**: Simplest but loses conversation history on page refresh
   - **Rejected**: Poor user experience, violates requirement for conversation resumption
3. **Hybrid Approach (Cache + DB)**: Best performance but adds complexity
   - **Deferred**: Can optimize later if performance becomes issue

**Implementation Pattern**:

```python
# Conversation Memory Agent
from sqlmodel import Session, select
from backend.src.models import Conversation, Message
from datetime import datetime
import uuid

class ConversationMemoryAgent:
    """Agent responsible for persisting and retrieving conversation state"""

    def create_conversation(self, user_id: str, session: Session) -> str:
        """
        Create a new conversation session.
        Returns: conversation_id (UUID string)
        """
        conversation_id = str(uuid.uuid4())
        conversation = Conversation(
            id=conversation_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(conversation)
        session.commit()
        return conversation_id

    def save_message(self, conversation_id: str, user_id: str, role: str,
                    content: str, tool_calls: Optional[list], session: Session):
        """
        Save a message to the conversation.

        Args:
            conversation_id: UUID of the conversation
            user_id: Authenticated user ID
            role: "user" or "assistant"
            content: Message text
            tool_calls: List of tool calls (JSON) or None
            session: Database session
        """
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            tool_calls=tool_calls,  # JSON field
            created_at=datetime.utcnow()
        )
        session.add(message)
        session.commit()

    def get_conversation_history(self, conversation_id: str, user_id: str,
                                session: Session, limit: int = 20) -> list:
        """
        Retrieve conversation history (last N messages).

        Args:
            conversation_id: UUID of the conversation
            user_id: Authenticated user ID (for isolation check)
            session: Database session
            limit: Maximum messages to retrieve (default: 20)

        Returns:
            List of Message objects in chronological order

        Raises:
            PermissionError: If conversation doesn't belong to user
        """
        # Verify conversation ownership
        conversation = session.exec(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .where(Conversation.user_id == user_id)
        ).first()

        if not conversation:
            raise PermissionError(f"Conversation {conversation_id} not found or access denied")

        # Retrieve last N messages
        messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        ).all()

        # Return in chronological order (oldest first)
        return list(reversed(messages))
```

**Best Practices**:
- **Context Limits**: Retrieve only last 20 messages (≈10 exchanges) to prevent token overflow
- **Ownership Validation**: Always verify conversation belongs to authenticated user
- **Indexes**: Create indexes on `conversation_id` and `user_id` for fast queries
- **Retention Policy**: Archive old conversations after 90 days (future enhancement)
- **Pagination**: Support pagination for viewing full conversation history in UI

---

## 5. Frontend Chat UI Architecture

### Decision: Use React Hooks for State Management, No External Chat Library

**Rationale**:
- **Simplicity**: Custom components avoid dependencies and bundle bloat
- **Tailwind CSS**: Existing design system provides all styling utilities needed
- **TypeScript**: Type-safe state management with interfaces
- **Control**: Full control over UI/UX without library constraints

**Alternatives Considered**:
1. **React ChatKit Library**: Pre-built components but opinionated styling
   - **Rejected**: Tailwind CSS already provides all styling needed, avoid extra dependency
2. **Stream Chat React**: Feature-rich but overkill for simple task chatbot
   - **Rejected**: Over-engineered for our use case, includes features we don't need
3. **Custom Web Components**: Framework-agnostic but harder to integrate with Next.js
   - **Rejected**: React components are idiomatic for Next.js

**Implementation Pattern**:

```typescript
// hooks/useChat.ts
import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '@/lib/api-client';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  tool_calls?: ToolCall[];
  timestamp: string;
}

export interface ToolCall {
  tool: string;
  parameters: Record<string, any>;
  result: Record<string, any>;
}

export function useChat(userId: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    // Optimistic update: add user message immediately
    const userMessage: ChatMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.post(`/api/${userId}/chat`, {
        conversation_id: conversationId,
        message: content
      });

      // Update conversation ID if first message
      if (!conversationId) {
        setConversationId(response.data.conversation_id);
      }

      // Add assistant response
      const assistantMessage: ChatMessage = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: response.data.message,
        tool_calls: response.data.tool_calls,
        timestamp: response.data.timestamp
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to send message');
      // Remove optimistic user message on error
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  }, [userId, conversationId]);

  return {
    messages,
    conversationId,
    isLoading,
    error,
    sendMessage
  };
}
```

**Best Practices**:
- **Optimistic Updates**: Add user message to UI immediately for responsive feel
- **Error Recovery**: Remove optimistic message if API call fails
- **Loading States**: Show loading indicator while agent processes request
- **Markdown Support**: Use `react-markdown` library to render assistant responses with formatting
- **Auto-Scroll**: Scroll to bottom when new messages added
- **Accessibility**: Use semantic HTML (ARIA labels, keyboard navigation)

---

## 6. Database Schema Design

### Decision: Add Two New Tables (conversations, messages) with Proper Indexes

**Rationale**:
- **Normalization**: Separate conversations from messages for flexibility
- **User Isolation**: Both tables include `user_id` for filtering
- **Audit Trail**: created_at timestamps on all records
- **JSON Storage**: tool_calls stored as JSON for flexibility

**Schema**:

```sql
-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- Messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id UUID NOT NULL,
    user_id VARCHAR NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
```

**Best Practices**:
- **UUID for Conversations**: Use UUIDs instead of integers to prevent enumeration attacks
- **CASCADE DELETE**: Remove messages when conversation deleted
- **CHECK Constraints**: Ensure role is always 'user' or 'assistant'
- **JSONB for tool_calls**: PostgreSQL JSONB type allows querying tool results if needed
- **Indexes**: Critical for performance with large message volumes

---

## 7. Error Handling and User Feedback

### Decision: Translate All Technical Errors into User-Friendly Messages

**Rationale**:
- **User Experience**: Non-technical users shouldn't see stack traces or database errors
- **Security**: Don't expose internal system details that could aid attackers
- **Consistency**: All errors follow same format for frontend parsing

**Error Translation Map**:

| Technical Error | User-Friendly Message |
|----------------|----------------------|
| `PermissionError` (user_id mismatch) | "You don't have access to that task." |
| `NotFoundError` (task not found) | "I couldn't find task #{task_id}. Please check the task number and try again." |
| `ValidationError` (empty title) | "Task title is required. Please provide a name for your task." |
| `IntegrityError` (foreign key violation) | "I couldn't complete that operation. Please try again." |
| `CohereAPIError` (rate limit) | "I'm getting too many requests right now. Please wait a moment and try again." |
| `DatabaseConnectionError` | "I'm having trouble connecting right now. Please try again in a moment." |
| `TimeoutError` | "That's taking longer than expected. Please try again." |
| `UnknownIntentError` | "I'm not sure what you want to do. Try 'add task', 'show tasks', 'complete task', or 'delete task'." |

**Implementation**:

```python
# Error handling decorator
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def handle_tool_errors(func):
    """Decorator to translate technical errors into user-friendly messages"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PermissionError as e:
            logger.warning(f"Permission denied: {e}")
            return {"error": "You don't have access to that task."}
        except NotFoundError as e:
            logger.info(f"Resource not found: {e}")
            return {"error": f"I couldn't find that task. Please check the task number and try again."}
        except ValidationError as e:
            logger.info(f"Validation failed: {e}")
            return {"error": str(e)}  # Validation errors are already user-friendly
        except CohereAPIError as e:
            logger.error(f"Cohere API error: {e}")
            return {"error": "I'm having trouble understanding right now. Please try again."}
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return {"error": "I'm having trouble right now. Please try again in a moment."}
    return wrapper
```

---

## Research Summary

All technical decisions documented and ready for Phase 1 design:

✅ **Cohere API Integration**: Use Command model for intent classification and entity extraction with structured prompts
✅ **OpenAI Agents SDK**: Custom Cohere model provider replaces default Gemini/OpenAI
✅ **MCP Tools**: Standalone functions with Pydantic validation and SQLModel database operations
✅ **Stateless Architecture**: Conversation history retrieved from database on every request
✅ **Frontend Chat UI**: Custom React components with hooks for state management, no external chat library
✅ **Database Schema**: Two new tables (conversations, messages) with proper indexes and user isolation
✅ **Error Handling**: Comprehensive translation map for user-friendly error messages

**Next Phase**: Phase 1 Design (data-model.md, contracts/, quickstart.md)
