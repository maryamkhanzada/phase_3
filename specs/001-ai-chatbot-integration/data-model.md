# Data Model: AI Todo Chatbot Integration

**Feature**: AI Todo Chatbot Integration
**Branch**: `001-ai-chatbot-integration`
**Date**: 2026-01-14
**Phase**: Phase 1 - Data Model Design

## Purpose

This document defines the data entities, relationships, and constraints for the AI Todo Chatbot feature. All entities support user isolation and stateless backend architecture.

---

## Entity Overview

The chatbot integration introduces two new entities:
1. **Conversation**: Represents a chat session between a user and the AI chatbot
2. **Message**: Represents individual messages within a conversation (user and assistant)

Existing entities:
- **User**: Managed by Better Auth (no changes required)
- **Task**: Existing task entity (no schema changes, used by MCP tools)

---

## Entity Definitions

### 1. Conversation

**Purpose**: Represents a chat session between a user and the chatbot. Each conversation has a unique ID and tracks when it was created and last updated.

**Fields**:

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | UUID (String) | PRIMARY KEY, NOT NULL | Unique conversation identifier (UUID v4) |
| `user_id` | String | NOT NULL, FOREIGN KEY → users.id | Owner of the conversation |
| `created_at` | DateTime | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When conversation was created |
| `updated_at` | DateTime | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last message timestamp |

**Relationships**:
- **One-to-Many** with Message: A conversation contains many messages
- **Many-to-One** with User: A user can have multiple conversations

**Indexes**:
- Primary key on `id`
- Index on `user_id` for filtering user's conversations
- Index on `updated_at DESC` for sorting by recent activity

**Validation Rules**:
- `id` must be valid UUID v4 format
- `user_id` must reference existing user
- `created_at` ≤ `updated_at`

**SQLModel Definition**:

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
import uuid

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique conversation identifier"
    )
    user_id: str = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="Owner of the conversation"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When conversation was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Last message timestamp"
    )

    # Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

**State Transitions**: None (conversations don't have state beyond timestamps)

**Business Rules**:
1. Users can only access their own conversations (enforced by `user_id` filter)
2. Conversations persist indefinitely (no automatic deletion)
3. Deleting a conversation cascades to all its messages
4. `updated_at` is updated whenever a new message is added

---

### 2. Message

**Purpose**: Represents a single message in a conversation. Messages can be from the user or the assistant. Assistant messages may include tool calls (task operations).

**Fields**:

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique message identifier |
| `conversation_id` | UUID (String) | NOT NULL, FOREIGN KEY → conversations.id | Parent conversation |
| `user_id` | String | NOT NULL, FOREIGN KEY → users.id | Owner of the message (for isolation) |
| `role` | String | NOT NULL, CHECK (role IN ('user', 'assistant')) | Message sender role |
| `content` | Text | NOT NULL | Message text content |
| `tool_calls` | JSON (JSONB in Postgres) | NULLABLE | Array of tool calls executed (assistant only) |
| `created_at` | DateTime | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When message was created |

**Relationships**:
- **Many-to-One** with Conversation: Many messages belong to one conversation
- **Many-to-One** with User: Many messages belong to one user (for isolation)

**Indexes**:
- Primary key on `id`
- Index on `conversation_id` for retrieving conversation history
- Index on `user_id` for user isolation checks
- Index on `created_at DESC` for chronological ordering

**Validation Rules**:
- `role` must be either 'user' or 'assistant'
- `content` must not be empty (min length: 1)
- `tool_calls` only populated for assistant messages (null for user messages)
- `conversation_id` must reference existing conversation
- `user_id` must match conversation's `user_id` (referential integrity)

**SQLModel Definition**:

```python
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON, CheckConstraint
from datetime import datetime
from typing import Optional, List, Dict, Any

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Unique message identifier"
    )
    conversation_id: str = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True,
        description="Parent conversation"
    )
    user_id: str = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="Owner of the message"
    )
    role: str = Field(
        nullable=False,
        description="Message sender role (user or assistant)"
    )
    content: str = Field(
        nullable=False,
        description="Message text content"
    )
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Array of tool calls executed (assistant only)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="When message was created"
    )

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")

    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name="check_role"),
        CheckConstraint("LENGTH(content) > 0", name="check_content_not_empty"),
    )
```

**State Transitions**: None (messages are immutable once created)

**Business Rules**:
1. Messages are immutable (no updates after creation)
2. User messages never have `tool_calls` (always null)
3. Assistant messages may have `tool_calls` if MCP tools were executed
4. Messages belong to exactly one conversation
5. Message `user_id` must match conversation's `user_id`
6. Messages ordered by `created_at` in chronological order

**Tool Calls Structure** (JSON):

```json
[
  {
    "tool": "add_task",
    "parameters": {
      "user_id": "user_xyz",
      "title": "buy groceries",
      "description": null,
      "completed": false
    },
    "result": {
      "id": 42,
      "user_id": "user_xyz",
      "title": "buy groceries",
      "description": null,
      "completed": false,
      "created_at": "2026-01-14T20:00:00Z",
      "updated_at": "2026-01-14T20:00:00Z"
    }
  }
]
```

---

## Entity Relationships Diagram

```
┌─────────────────┐
│     User        │ (Existing - managed by Better Auth)
│                 │
│ - id (PK)       │
│ - email         │
│ - name          │
│ - created_at    │
└────────┬────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────┐
│  Conversation   │ (NEW)
│                 │
│ - id (PK, UUID) │◄─────┐
│ - user_id (FK)  │      │
│ - created_at    │      │
│ - updated_at    │      │
└────────┬────────┘      │
         │               │
         │ 1:N           │
         │               │
         ▼               │
┌─────────────────┐      │
│    Message      │ (NEW)│
│                 │      │
│ - id (PK)       │      │
│ - conversation_id (FK)─┘
│ - user_id (FK)  │
│ - role          │
│ - content       │
│ - tool_calls    │
│ - created_at    │
└─────────────────┘

┌─────────────────┐
│      Task       │ (Existing - used by MCP tools)
│                 │
│ - id (PK)       │
│ - user_id (FK)  │◄───── References same user
│ - title         │
│ - description   │
│ - completed     │
│ - created_at    │
│ - updated_at    │
└─────────────────┘
```

**Relationship Notes**:
- **User ↔ Conversation**: One user can have many conversations (1:N)
- **Conversation ↔ Message**: One conversation can have many messages (1:N)
- **User ↔ Message**: One user can have many messages (1:N, for isolation)
- **Task**: No direct relationship to Conversation/Message, accessed via MCP tools only

---

## Database Constraints

### Foreign Key Constraints

1. **Conversation.user_id** → **User.id**
   - Action on delete: CASCADE (remove conversations when user deleted)
   - Action on update: CASCADE

2. **Message.conversation_id** → **Conversation.id**
   - Action on delete: CASCADE (remove messages when conversation deleted)
   - Action on update: CASCADE

3. **Message.user_id** → **User.id**
   - Action on delete: CASCADE (remove messages when user deleted)
   - Action on update: CASCADE

### Check Constraints

1. **Message.role**: Must be 'user' or 'assistant'
2. **Message.content**: Must have length > 0 (not empty)
3. **Conversation.created_at** ≤ **Conversation.updated_at** (enforced in application logic)

### Unique Constraints

None required (conversations and messages don't have natural unique identifiers beyond primary keys)

---

## Indexes

### Performance Indexes

1. **conversations.user_id** (B-tree): Fast lookup of user's conversations
2. **conversations.updated_at** (B-tree DESC): Sort conversations by recent activity
3. **messages.conversation_id** (B-tree): Fast retrieval of conversation history
4. **messages.user_id** (B-tree): User isolation checks
5. **messages.created_at** (B-tree DESC): Chronological message ordering

### Index Rationale

- **user_id indexes**: Enable fast filtering by authenticated user (user isolation)
- **conversation_id index**: Critical for retrieving conversation history (most frequent query)
- **created_at indexes**: Support ORDER BY clauses for chronological display
- **No full-text indexes**: Messages not searched by content in Phase III (future enhancement)

---

## Database Migrations

### Migration 1: Create conversations table

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_conversations_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);
```

### Migration 2: Create messages table

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id UUID NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_messages_conversation_id FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    CONSTRAINT fk_messages_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT check_role CHECK (role IN ('user', 'assistant')),
    CONSTRAINT check_content_not_empty CHECK (LENGTH(content) > 0)
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
```

---

## Data Access Patterns

### Common Queries

**1. Get user's conversations (sorted by recent activity)**

```sql
SELECT * FROM conversations
WHERE user_id = ?
ORDER BY updated_at DESC
LIMIT 20;
```

**2. Get conversation history (last 20 messages)**

```sql
SELECT * FROM messages
WHERE conversation_id = ? AND user_id = ?
ORDER BY created_at DESC
LIMIT 20;
```
*(Reversed in application code to display oldest-first)*

**3. Create new conversation**

```sql
INSERT INTO conversations (id, user_id, created_at, updated_at)
VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
```

**4. Save new message**

```sql
INSERT INTO messages (conversation_id, user_id, role, content, tool_calls, created_at)
VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP);
```

**5. Update conversation timestamp**

```sql
UPDATE conversations
SET updated_at = CURRENT_TIMESTAMP
WHERE id = ? AND user_id = ?;
```

### Query Performance Expectations

| Query | Expected Latency | Index Used |
|-------|------------------|------------|
| Get user's conversations | <50ms | idx_conversations_user_id + idx_conversations_updated_at |
| Get conversation history | <100ms | idx_messages_conversation_id + idx_messages_created_at |
| Create conversation | <20ms | Primary key |
| Save message | <30ms | Primary key + foreign keys |
| Update conversation timestamp | <20ms | Primary key |

---

## Data Validation

### Application-Level Validation (Pydantic)

**Conversation Creation**:
```python
from pydantic import BaseModel, Field, validator
import uuid

class ConversationCreate(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255)

    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or not v.strip():
            raise ValueError("user_id cannot be empty")
        return v.strip()
```

**Message Creation**:
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any

class MessageCreate(BaseModel):
    conversation_id: str = Field(..., description="UUID of conversation")
    user_id: str = Field(..., min_length=1, max_length=255)
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=10000)
    tool_calls: Optional[List[Dict[str, Any]]] = None

    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        return v.strip()

    @validator('tool_calls')
    def validate_tool_calls(cls, v, values):
        # Tool calls only allowed for assistant messages
        if v is not None and values.get('role') != 'assistant':
            raise ValueError("tool_calls only allowed for assistant messages")
        return v
```

---

## Data Model Summary

**New Entities**: 2
- Conversation (conversations table)
- Message (messages table)

**New Indexes**: 5
- conversations.user_id
- conversations.updated_at
- messages.conversation_id
- messages.user_id
- messages.created_at

**Foreign Key Relationships**: 3
- Conversation → User
- Message → Conversation
- Message → User

**Check Constraints**: 2
- Message.role IN ('user', 'assistant')
- Message.content LENGTH > 0

**All entities enforce user isolation via user_id field and indexes.**

**Next Phase**: API Contracts (contracts/chat-api.yaml, contracts/mcp-tools.yaml)
