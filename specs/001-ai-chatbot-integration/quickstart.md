# Quickstart Guide: AI Todo Chatbot Integration

**Feature**: AI Todo Chatbot Integration
**Branch**: `001-ai-chatbot-integration`
**Date**: 2026-01-14
**Phase**: Phase 1 - Quickstart Guide

## Purpose

This guide provides step-by-step instructions for developers to set up, develop, and test the AI Todo Chatbot integration. Follow this guide to go from initial setup to running the chatbot locally.

---

## Prerequisites

### Required Software
- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **PostgreSQL**: 14+ (Neon Serverless or local)
- **Git**: Latest version

### Required Accounts
- **Cohere API Account**: Sign up at https://cohere.com/ and obtain API key
- **Neon Database Account**: Sign up at https://neon.tech/ and create database

### Development Tools
- **Code Editor**: VS Code recommended (with Python and TypeScript extensions)
- **API Testing Tool**: Postman, Insomnia, or curl
- **Database Client**: pgAdmin, DBeaver, or psql command-line

---

## Step 1: Environment Setup

### 1.1 Clone Repository

```bash
# If not already cloned
git clone <repository-url>
cd frontend_todo_app

# Checkout feature branch
git checkout 001-ai-chatbot-integration
```

### 1.2 Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install new chatbot dependencies
pip install cohere openai-agents-sdk
```

### 1.3 Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# No additional packages needed (React, Tailwind, Better Auth already installed)
```

### 1.4 Configure Environment Variables

**Backend `.env`**:

```bash
cd ../backend

# Copy example and edit
cp .env.example .env

# Edit .env with your values:
DATABASE_URL=postgresql://user:password@host/database  # Neon connection string
BETTER_AUTH_SECRET=your-jwt-secret-key-here
COHERE_API_KEY=your-cohere-api-key-here
CORS_ORIGINS=http://localhost:3000
PORT=8000
```

**Frontend `.env.local`**:

```bash
cd ../frontend

# Edit .env.local with your values:
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-jwt-secret-key-here  # Same as backend
```

---

## Step 2: Database Setup

### 2.1 Run Migrations

```bash
cd ../backend

# Apply existing migrations (users, tasks tables)
# (Migration commands depend on your migration tool - Alembic, SQLModel, etc.)

# Apply new chatbot migrations
# Migration 1: Create conversations table
psql $DATABASE_URL -f migrations/001_create_conversations.sql

# Migration 2: Create messages table
psql $DATABASE_URL -f migrations/002_create_messages.sql
```

### 2.2 Verify Tables

```sql
-- Connect to database
psql $DATABASE_URL

-- Verify tables exist
\dt

-- Should see:
-- users
-- tasks
-- conversations
-- messages

-- Verify indexes
\di

-- Should see indexes on:
-- conversations.user_id
-- conversations.updated_at
-- messages.conversation_id
-- messages.user_id
-- messages.created_at
```

---

## Step 3: Backend Development

### 3.1 Implement Database Models

**File**: `backend/src/models.py`

```python
# Add to existing models.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
import uuid

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    messages: List["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id", nullable=False, index=True)
    user_id: str = Field(foreign_key="users.id", nullable=False, index=True)
    role: str = Field(nullable=False)  # 'user' or 'assistant'
    content: str = Field(nullable=False)
    tool_calls: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

### 3.2 Implement Cohere Service

**File**: `backend/src/services/cohere_service.py`

```python
import cohere
from backend.src.config import settings

class CohereService:
    def __init__(self):
        self.client = cohere.Client(api_key=settings.COHERE_API_KEY)

    def classify_intent(self, message: str) -> str:
        """Classify user message into task intent"""
        # Implementation from research.md
        pass

    def extract_entities(self, message: str, intent: str) -> dict:
        """Extract task entities from message"""
        # Implementation from research.md
        pass

cohere_service = CohereService()
```

### 3.3 Implement MCP Tools

**File**: `backend/src/agents/mcp_tools.py`

```python
from pydantic import BaseModel, Field
from backend.src.db import get_session
from backend.src.models import Task

class AddTaskParams(BaseModel):
    user_id: str
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: bool = False

def add_task(params: AddTaskParams):
    """MCP Tool: Create new task"""
    # Implementation from research.md
    pass

# Implement: list_tasks, update_task, complete_task, delete_task
```

### 3.4 Implement Chat Endpoint

**File**: `backend/src/routes/chat.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from backend.src.auth.jwt import get_current_user
from backend.src.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()

@router.post("/api/{user_id}/chat")
async def send_chat_message(
    user_id: str,
    request: ChatRequest,
    current_user: str = Depends(get_current_user)
):
    # Verify user_id matches JWT
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Permission denied")

    # Process message with orchestrator agent
    # Implementation from research.md
    pass
```

### 3.5 Register Chat Routes

**File**: `backend/src/main.py`

```python
# Add to existing main.py
from backend.src.routes import chat

app.include_router(chat.router)
```

---

## Step 4: Frontend Development

### 4.1 Create Chat Types

**File**: `frontend/src/types/chat.ts`

```typescript
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
  result: any;
}

export interface ChatRequest {
  conversation_id?: string;
  message: string;
}

export interface ChatResponse {
  conversation_id: string;
  message: string;
  tool_calls?: ToolCall[];
  timestamp: string;
}
```

### 4.2 Implement useChat Hook

**File**: `frontend/src/hooks/useChat.ts`

```typescript
// Implementation from research.md
import { useState, useCallback } from 'react';
import { apiClient } from '@/lib/api-client';

export function useChat(userId: string) {
  // Implementation details...
}
```

### 4.3 Create Chat Components

**File**: `frontend/src/components/chat/ChatIcon.tsx`

```typescript
'use client';

export function ChatIcon({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 rounded-full shadow-lg hover:bg-blue-700 flex items-center justify-center"
      aria-label="Open chat"
    >
      {/* Chat icon SVG */}
    </button>
  );
}
```

**File**: `frontend/src/components/chat/ChatPopup.tsx`

```typescript
'use client';

import { useChat } from '@/hooks/useChat';

export function ChatPopup({ userId, onClose }: Props) {
  const { messages, isLoading, sendMessage } = useChat(userId);

  return (
    <div className="fixed bottom-24 right-6 w-96 h-[600px] bg-white rounded-lg shadow-2xl flex flex-col">
      {/* Chat UI implementation */}
    </div>
  );
}
```

### 4.4 Add Chat to Layout

**File**: `frontend/src/app/layout.tsx`

```typescript
'use client';

import { ChatIcon } from '@/components/chat/ChatIcon';
import { ChatPopup } from '@/components/chat/ChatPopup';
import { useState } from 'react';

export default function RootLayout({ children }: Props) {
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <html lang="en">
      <body>
        {children}
        <ChatIcon onClick={() => setIsChatOpen(true)} />
        {isChatOpen && <ChatPopup userId={user.id} onClose={() => setIsChatOpen(false)} />}
      </body>
    </html>
  );
}
```

---

## Step 5: Run and Test

### 5.1 Start Backend Server

```bash
cd backend

# Activate virtual environment if not already active
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run FastAPI server
uvicorn src.main:app --reload --port 8000

# Server should start at http://localhost:8000
# Verify: curl http://localhost:8000/health
```

### 5.2 Start Frontend Dev Server

```bash
cd ../frontend

# Run Next.js development server
npm run dev

# Frontend should start at http://localhost:3000
```

### 5.3 Test Basic Functionality

**Manual Testing**:

1. **Open browser**: Navigate to http://localhost:3000
2. **Login**: Authenticate with Better Auth
3. **Click chat icon**: Fixed in bottom-right corner
4. **Send test messages**:
   - "Add a task to buy groceries"
   - "Show me my tasks"
   - "Mark task 1 as complete"
   - "Delete task 2"

**Expected Results**:
- Chat popup opens when icon clicked
- User messages appear immediately (optimistic update)
- Assistant responses appear within 2-3 seconds
- Task operations execute correctly (verify in task list)
- Error messages are user-friendly

**API Testing with curl**:

```bash
# Get JWT token first (from login endpoint)
export TOKEN="your-jwt-token-here"
export USER_ID="your-user-id-here"

# Send chat message
curl -X POST http://localhost:8000/api/$USER_ID/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}'

# Expected response:
# {
#   "conversation_id": "conv_...",
#   "message": "I've added 'buy groceries' to your task list.",
#   "tool_calls": [...],"
#   "timestamp": "2026-01-14T20:00:00Z"
# }
```

---

## Step 6: Debugging

### Common Issues

**Issue**: "Cohere API key not found"
- **Solution**: Check `.env` file has `COHERE_API_KEY` set correctly
- **Verify**: `echo $COHERE_API_KEY` (Unix) or `echo %COHERE_API_KEY%` (Windows)

**Issue**: "Database connection failed"
- **Solution**: Verify `DATABASE_URL` in `.env` is correct
- **Test**: `psql $DATABASE_URL -c "SELECT 1"`

**Issue**: "JWT verification failed"
- **Solution**: Ensure `BETTER_AUTH_SECRET` matches in backend and frontend `.env` files

**Issue**: "Chat icon not visible"
- **Solution**: Check browser console for errors, verify ChatIcon component imported correctly

**Issue**: "Intent classification always returns 'unknown'"
- **Solution**: Check Cohere API quota, verify few-shot examples in `classify_intent()`

### Logging

**Backend Logging**:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In chat endpoint:
logger.info(f"Received message from user {user_id}: {request.message}")
logger.info(f"Classified intent: {intent}")
logger.info(f"Extracted entities: {entities}")
logger.info(f"Tool calls: {tool_calls}")
```

**Frontend Logging**:

```typescript
// In useChat hook:
console.log('Sending message:', content);
console.log('Received response:', response.data);
console.log('Tool calls:', response.data.tool_calls);
```

### Database Inspection

```sql
-- View conversations
SELECT * FROM conversations ORDER BY updated_at DESC LIMIT 10;

-- View messages for a conversation
SELECT * FROM messages WHERE conversation_id = 'conv_...' ORDER BY created_at;

-- View recent tool calls
SELECT role, content, tool_calls FROM messages WHERE tool_calls IS NOT NULL ORDER BY created_at DESC LIMIT 10;
```

---

## Step 7: Next Steps

After basic functionality is working:

1. **Implement All User Stories**:
   - ✅ P1: Natural language task creation
   - ⬜ P2: View and query tasks
   - ⬜ P3: Complete and update tasks
   - ⬜ P4: Delete tasks with confirmation
   - ⬜ P5: Multi-step commands

2. **Add Error Handling**:
   - Cohere API rate limit handling
   - Network timeout recovery
   - Invalid input validation

3. **Improve UI/UX**:
   - Markdown rendering in chat messages
   - Task result formatting (tables, lists)
   - Loading animations
   - Keyboard shortcuts (Enter to send)

4. **Run Performance Tests**:
   - Measure response time (should be <3s p95)
   - Test concurrent conversations
   - Monitor Cohere API token usage

5. **Write Tests** (optional):
   - Unit tests for MCP tools
   - Integration tests for chat endpoint
   - Frontend component tests

6. **Document Configuration**:
   - Update README with setup instructions
   - Document environment variables
   - Add troubleshooting guide

---

## Resources

- **Cohere Documentation**: https://docs.cohere.com/
- **OpenAI Agents SDK**: https://github.com/openai/agents-sdk (hypothetical, adjust to actual SDK)
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Next.js Documentation**: https://nextjs.org/docs

---

## Getting Help

**Development Questions**:
1. Check `specs/001-ai-chatbot-integration/research.md` for technical decisions
2. Review `specs/001-ai-chatbot-integration/data-model.md` for schema details
3. Consult `specs/001-ai-chatbot-integration/contracts/` for API specifications

**Error Resolution**:
1. Check backend logs: `backend/logs/app.log`
2. Check frontend console: Browser DevTools → Console
3. Inspect database: `psql $DATABASE_URL`
4. Test API directly: Use curl or Postman

**Ready for Implementation**:
- All planning artifacts complete
- Run `/sp.tasks` to generate implementation tasks
- Start with P1 user story (natural language task creation)
