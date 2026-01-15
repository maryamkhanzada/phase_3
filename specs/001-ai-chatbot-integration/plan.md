# Implementation Plan: AI Todo Chatbot Integration

**Branch**: `001-ai-chatbot-integration` | **Date**: 2026-01-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ai-chatbot-integration/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Integrate an AI-powered chatbot into the Todo Full-Stack Web Application to enable natural language task management. Users interact with a chat interface (fixed icon + popup) to create, query, update, complete, and delete tasks using conversational commands. The system uses Cohere API for NLP (intent classification, entity extraction) and OpenAI Agents SDK for agent orchestration. Three specialized agents (Todo-Orchestrator, Task-Ops-Executor, Conversation-Memory) coordinate to process user messages, execute MCP tools for task operations, and persist conversation history in PostgreSQL. The backend remains stateless with all conversation context retrieved from the database on each request to support horizontal scaling.

**Technical Approach**:
- Frontend: Add chat UI component with fixed icon (bottom-right) that opens popup interface
- Backend: Implement `/api/{user_id}/chat` endpoint with JWT authentication
- Agents: Three-agent architecture using OpenAI Agents SDK with Cohere as NLP provider
- MCP Tools: Five tools (add_task, list_tasks, update_task, complete_task, delete_task) enforce user isolation
- Database: Add conversations and messages tables with indexes for performant queries
- NLP: Cohere API handles intent classification and entity extraction from natural language
- Persistence: All conversation state stored in database (no in-memory state)

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/Next.js 16+ (frontend)

**Primary Dependencies**:
- **Backend**: FastAPI, SQLModel, Cohere Python SDK, OpenAI Agents SDK, Pydantic, python-jose (JWT), psycopg2-binary (PostgreSQL driver)
- **Frontend**: Next.js 16+ (App Router), React 19, TypeScript, Tailwind CSS, Better Auth, Axios/Fetch

**Storage**: Neon Serverless PostgreSQL (existing tasks table + new conversations and messages tables)

**Testing**: pytest (backend), Jest/React Testing Library (frontend) - tests optional per spec

**Target Platform**: Web application (server-side: Linux/Docker containers, client-side: modern browsers)

**Project Type**: Web application (monorepo structure with separate backend/ and frontend/ directories)

**Performance Goals**:
- Chat response time: <3 seconds at 95th percentile
- Intent classification accuracy: >90% for standard phrasing
- Task operation success rate: >95%
- Support 100+ concurrent chat sessions without degradation
- Database query time: <100ms for conversation history retrieval

**Constraints**:
- Stateless backend architecture (no in-memory conversation state)
- Cohere API token limits: conversation history truncated to last 20 messages
- JWT authentication required on all chatbot endpoints
- User isolation enforced at database layer for all operations
- CORS must allow frontend origin for chat API
- Conversation history limited to prevent excessive token usage

**Scale/Scope**:
- Target: 1,000+ users with 10,000+ tasks across user base
- Average conversation length: 5-10 message exchanges
- Expected conversation volume: 50-100 new conversations per day
- Task database: existing, supports user isolation
- New tables: conversations (low volume), messages (moderate volume with retention policy TBD)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-First Development (MANDATORY)

✅ **PASS**: Feature spec exists at `specs/001-ai-chatbot-integration/spec.md` with 5 user stories, 20 functional requirements, and 10 success criteria. All chatbot behaviors documented before implementation.

**Action**: None required

---

### Principle II: Authentication & Security (STRICT)

✅ **PASS**: JWT authentication enforced on `/api/{user_id}/chat` endpoint. User isolation verified for all task operations via MCP tools. Cohere API key stored in `.env` as `COHERE_API_KEY`.

**Validation checklist**:
- [ ] Chat endpoint validates JWT before processing messages
- [ ] User ID extracted from JWT, not trusted from URL/body
- [ ] MCP tools filter all task queries by authenticated `user_id`
- [ ] Conversation and message records include `user_id` for isolation
- [ ] Unauthenticated chat requests return HTTP 401
- [ ] Cross-user conversation access returns HTTP 403

**Action**: Implement JWT dependency injection for chat endpoint, enforce user_id filtering in all MCP tools

---

### Principle III: API Design & RESTful Standards

✅ **PASS**: Chatbot endpoint follows pattern `/api/{user_id}/chat` with POST method. Errors return structured JSON `{ "error": "message" }`. Status codes semantically correct (200, 400, 401, 403, 500).

**API Contract**:
- **Endpoint**: `POST /api/{user_id}/chat`
- **Request**: `{ "conversation_id": "optional", "message": "string" }`
- **Response**: `{ "conversation_id": "string", "message": "string", "tool_calls": [...], "timestamp": "ISO8601" }`
- **Error Formats**: Defined in spec for 400, 401, 403, 500

**Action**: Document endpoint in `specs/001-ai-chatbot-integration/contracts/chat-api.yaml`

---

### Principle IV: Data Ownership & User Isolation

✅ **PASS**: Conversations and messages tables include `user_id`. All database queries filter by authenticated `user_id`. MCP tools enforce ownership checks.

**Isolation checklist**:
- [ ] conversations table has `user_id` column with NOT NULL constraint
- [ ] messages table has `user_id` column with NOT NULL constraint
- [ ] Database queries use `WHERE user_id = ?` on all SELECT/UPDATE/DELETE
- [ ] Foreign key from messages.user_id to users.id enforces referential integrity
- [ ] Agent logic never bypasses MCP tools to access database directly

**Action**: Define schema with user_id constraints in `data-model.md`, implement ownership checks in MCP tools

---

### Principle V: Tech Stack Enforcement

✅ **PASS**: Stack matches constitution requirements:
- Frontend: Next.js 16+, TypeScript, Tailwind CSS, Better Auth
- Backend: FastAPI, SQLModel, Python 3.11+
- AI/NLP: Cohere API, OpenAI Agents SDK
- Database: PostgreSQL (Neon)
- MCP Tools: Custom implementation

**No violations detected**

---

### Principle VI: Instruction Hierarchy

✅ **PASS**: Implementation follows:
1. Spec document (highest priority)
2. Root CLAUDE.md
3. Constitution (this check)

**No conflicts detected**

---

### Principle VII: Phase-Aware Implementation

✅ **PASS**: Feature is Phase III as defined in constitution. Includes all required features:
- Natural language task management ✓
- Agent-based architecture (3 agents) ✓
- MCP tools for task operations ✓
- Conversation persistence ✓
- Cohere API integration ✓
- OpenAI Agents SDK integration ✓
- ChatKit/custom chat UI ✓

**Out-of-scope items correctly excluded**:
- Voice-based interactions ✓
- Multi-language support ✓
- Third-party integrations ✓
- Real-time collaboration ✓
- Mobile native apps ✓

**Action**: None required

---

### Principle VIII: AI Agent Architecture (NEW)

✅ **PASS**: Three agents with clear separation of concerns:
1. **Todo-Orchestrator Agent**: Receives messages, detects intent, extracts entities, selects MCP tools, generates responses
2. **Task-Ops-Executor Agent**: Implements MCP tools, enforces user isolation, performs SQLModel operations
3. **Conversation-Memory Agent**: Persists chat history, maintains conversation_id, tracks messages

**Agent rules**:
- [ ] Agents operate within defined skills (to be documented in `specs/skills/`)
- [ ] Agents do NOT directly access database (use MCP tools or service layers)
- [ ] Todo-Orchestrator decides tool invocation based on intent
- [ ] Task-Ops-Executor enforces user isolation on all DB operations
- [ ] Conversation-Memory manages all conversation state
- [ ] Agent outputs deterministic and reproducible
- [ ] Structured JSON for all MCP tool calls
- [ ] Error handling translates technical errors to user-friendly messages

**Action**: Document agent responsibilities in `specs/agents/chatbot-agents.md`, define skills in `specs/skills/chatbot-skills.md`

---

### Principle IX: MCP Tools & Agent Orchestration (NEW)

✅ **PASS**: Five MCP tools defined:
- `add_task(user_id, title, description, completed)` → Creates task
- `list_tasks(user_id, completed=None)` → Retrieves tasks with optional filter
- `update_task(user_id, task_id, title=None, description=None)` → Updates task
- `complete_task(user_id, task_id, completed)` → Toggles completion
- `delete_task(user_id, task_id)` → Deletes task

**MCP rules**:
- [ ] All tools enforce `user_id` validation (owner checks)
- [ ] Tools are ONLY way agents interact with task data
- [ ] Tools validate all inputs and return structured errors
- [ ] Tools use SQLModel for all database operations
- [ ] Tool responses consistent JSON structures
- [ ] OpenAI Agents SDK orchestrates tool selection
- [ ] Agents handle tool errors gracefully
- [ ] Tool calls logged for debugging and audit

**Action**: Implement MCP tools in `backend/src/agents/mcp_tools.py`, integrate with Agents SDK

---

### Principle X: Conversation Memory & Stateless Architecture (NEW)

✅ **PASS**: Stateless backend design:
- Backend servers maintain no in-memory conversation state
- Every conversation has unique `conversation_id`
- All messages persisted in `messages` table
- Conversation history retrieved from database on every request
- Conversation-Memory Agent manages all persistence
- Multiple concurrent conversations per user supported
- Conversation resumption after server restarts enabled

**Stateless checklist**:
- [ ] No global/module-level conversation caches in backend code
- [ ] Chat endpoint retrieves conversation history from DB on each request
- [ ] Conversation context limited to last 20 messages (10 exchanges)
- [ ] Old conversations archived but not deleted (audit trail)

**Action**: Implement stateless retrieval logic in Conversation-Memory Agent, document context management strategy

---

### Principle XI: AI/NLP Integration (NEW)

✅ **PASS**: Cohere API and OpenAI Agents SDK integration:

**Cohere API Usage**:
- Intent classification (detect: add, list, update, complete, delete)
- Entity extraction (extract: task_id, title, description, status)
- Semantic embeddings (future: task search and similarity)
- Text generation (user-friendly responses)

**OpenAI Agents SDK Usage**:
- Agent logic orchestration (tool selection, parameter preparation)
- Multi-step workflow execution (tool chaining)
- Decision-making based on Cohere embeddings
- Structured output generation

**Integration rules**:
- [ ] Cohere API key in `.env` as `COHERE_API_KEY`
- [ ] OpenAI Agents SDK config uses environment variables
- [ ] API keys NEVER hardcoded or committed to version control
- [ ] Use Cohere for all NLP tasks (no duplication with other services)
- [ ] OpenAI Agents SDK runs on top of Cohere embeddings
- [ ] Handle API rate limits and errors gracefully
- [ ] Cache embeddings where appropriate to reduce costs
- [ ] Log all API calls for debugging and cost tracking

**Action**: Configure Cohere client in `backend/src/services/cohere_service.py`, integrate with Agents SDK in `backend/src/agents/orchestrator.py`

---

### Constitution Check Summary

**Total Gates**: 11
**Passed**: 11 ✅
**Failed**: 0 ❌
**Warnings**: 0 ⚠️

**Proceed to Phase 0 Research**: ✅ APPROVED

---

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-chatbot-integration/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── chat-api.yaml    # Chat endpoint OpenAPI spec
│   └── mcp-tools.yaml   # MCP tools schema definitions
├── spec.md              # Feature specification (already created)
└── checklists/
    └── requirements.md  # Specification quality checklist (already created)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── agents/                    # NEW: AI agent implementations
│   │   ├── __init__.py
│   │   ├── orchestrator.py        # Todo-Orchestrator Agent
│   │   ├── task_executor.py       # Task-Ops-Executor Agent
│   │   ├── conversation_memory.py # Conversation-Memory Agent
│   │   └── mcp_tools.py           # MCP tool implementations
│   ├── services/                  # NEW: External service integrations
│   │   ├── __init__.py
│   │   └── cohere_service.py      # Cohere API client wrapper
│   ├── routes/
│   │   ├── chat.py                # NEW: Chat endpoint
│   │   ├── auth.py                # Existing auth routes
│   │   └── tasks.py               # Existing task routes
│   ├── models.py                  # EXTEND: Add Conversation, Message models
│   ├── schemas/
│   │   └── chat.py                # NEW: Chat request/response schemas
│   ├── auth/
│   │   └── jwt.py                 # Existing JWT verification
│   ├── db.py                      # Existing database connection
│   ├── config.py                  # EXTEND: Add Cohere API key config
│   └── main.py                    # EXTEND: Register chat routes
└── tests/                         # OPTIONAL: Add agent and chat tests

frontend/
├── src/
│   ├── components/
│   │   ├── chat/                  # NEW: Chat UI components
│   │   │   ├── ChatIcon.tsx       # Fixed chat icon (bottom-right)
│   │   │   ├── ChatPopup.tsx      # Popup chat interface
│   │   │   ├── ChatMessage.tsx    # Individual message component
│   │   │   └── ChatInput.tsx      # Message input field
│   │   ├── tasks/                 # Existing task components
│   │   └── layouts/               # Existing layout components
│   ├── lib/
│   │   └── api-client.ts          # EXTEND: Add chat API methods
│   ├── types/
│   │   └── chat.ts                # NEW: Chat types (Message, Conversation, etc.)
│   ├── hooks/
│   │   └── useChat.ts             # NEW: Chat state management hook
│   └── app/
│       └── layout.tsx             # EXTEND: Add ChatIcon to global layout
└── public/                        # Existing static assets
```

**Structure Decision**: Web application structure (Option 2) selected. Existing monorepo with `backend/` and `frontend/` directories. Backend uses FastAPI with modular structure (routes, models, services, agents). Frontend uses Next.js App Router with component-based architecture. New additions:
- Backend: `agents/` directory for AI agents, `services/` for Cohere integration, `routes/chat.py` for endpoint
- Frontend: `components/chat/` for UI, `hooks/useChat.ts` for state, `types/chat.ts` for TypeScript definitions
- Database: Migrations will add conversations and messages tables

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution principles passed.

---

