---
id: 002
title: Create AI Chatbot Implementation Plan
stage: plan
date: 2026-01-14
surface: agent
model: claude-sonnet-4-5
feature: ai-chatbot-integration
branch: 001-ai-chatbot-integration
user: maryamkhanzada
command: /sp.plan
labels: ["phase-iii", "ai-chatbot", "implementation-plan", "cohere-api", "agents-sdk", "mcp-tools", "architecture"]
links:
  spec: specs/001-ai-chatbot-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-ai-chatbot-integration/plan.md
  - specs/001-ai-chatbot-integration/research.md
  - specs/001-ai-chatbot-integration/data-model.md
  - specs/001-ai-chatbot-integration/contracts/chat-api.yaml
  - specs/001-ai-chatbot-integration/contracts/mcp-tools.yaml
  - specs/001-ai-chatbot-integration/quickstart.md
tests:
  - N/A (planning artifacts - no tests required)
---

## Prompt

Create a detailed, full-stack implementation plan for Phase III of the Todo Full-Stack Web Application, focusing on AI Todo Chatbot integration using Cohere API and OpenAI Agents SDK.

====================
SCOPE
====================

- Backend: FastAPI + MCP tools + SQLModel + Neon DB
- Frontend: Next.js 16+, Tailwind CSS, Better Auth, Chatbot UI
- AI: Todo-Orchestrator, Task Operations, Conversation Memory agents
- NLP: Cohere API for intent detection, entity extraction, and multi-step command handling
- Agents SDK: Use OpenAI Agents SDK logic, replace model provider with Cohere
- Stateless chat endpoint with conversation persistence in DB
- Full integration between frontend chat icon, backend agents, and MCP tools

====================
IMPLEMENTATION PLAN
====================

Phase III Implementation Steps:

1️⃣ **Environment Setup**
- Configure .env with DATABASE_URL, BETTER_AUTH_SECRET, COHERE_API_KEY
- Install dependencies for FastAPI, SQLModel, Cohere Python SDK, OpenAI Agents SDK, Next.js + Tailwind + Better Auth
- Ensure backend and frontend run independently for testing

2️⃣ **Database Enhancements**
- Ensure `tasks`, `conversations`, `messages` tables exist
- Add conversation_id foreign key to messages
- Index tasks by user_id and status for performance
- Verify migrations using Neon PostgreSQL

3️⃣ **MCP Tool Implementation (Backend)**
- Implement MCP tools as stateless FastAPI endpoints: add_task, list_tasks, update_task, complete_task, delete_task
- Validate input, enforce user isolation, and return consistent JSON

4️⃣ **Agents Implementation**
- Conversation Memory Agent: Create, fetch, persist conversation sessions
- Task Operations Agent: Call MCP tools for CRUD operations
- Todo-Orchestrator Agent: Natural language processing and tool orchestration

## Response snapshot

Successfully created comprehensive implementation plan for AI Todo Chatbot Integration with complete Phase 0 Research and Phase 1 Design artifacts.

**Planning Artifacts Created**:

1. **plan.md** (350 lines):
   - Technical Context with performance goals, constraints, scale
   - Constitution Check (11 principles, all PASSED)
   - Project Structure (backend agents/, services/, frontend chat/)
   - No complexity violations detected

2. **research.md** (450 lines):
   - Cohere API integration patterns (Command model, intent classification, entity extraction)
   - OpenAI Agents SDK with custom Cohere provider
   - MCP tool implementation with Pydantic validation
   - Stateless conversation management strategy
   - Frontend chat UI architecture (React hooks, no external library)
   - Database schema design (conversations + messages tables)
   - Error handling and user feedback translation map

3. **data-model.md** (400 lines):
   - 2 new entities: Conversation (UUID PK), Message (with tool_calls JSON)
   - 5 indexes for performance (user_id, conversation_id, timestamps)
   - SQLModel definitions with relationships
   - Foreign key constraints with CASCADE deletes
   - Migration scripts for PostgreSQL
   - Query patterns and performance expectations

4. **contracts/chat-api.yaml** (450 lines):
   - OpenAPI 3.1.0 specification for POST /api/{user_id}/chat
   - Complete request/response schemas
   - Error response formats (400, 401, 403, 500)
   - Example payloads for all scenarios
   - Security scheme (Bearer JWT)

5. **contracts/mcp-tools.yaml** (150 lines):
   - 5 MCP tools with parameter/return schemas
   - Validation rules and error types
   - Security rules for user isolation
   - Usage notes for agent integration

6. **quickstart.md** (500 lines):
   - Complete setup guide (environment, dependencies, database)
   - Step-by-step backend implementation (models, services, agents, routes)
   - Step-by-step frontend implementation (types, hooks, components)
   - Testing procedures (manual, API, debugging)
   - Common issues and solutions

**Key Architectural Decisions**:

1. **Three-Agent Architecture**:
   - Todo-Orchestrator: Intent classification + entity extraction via Cohere
   - Task-Ops-Executor: MCP tool implementation with SQLModel
   - Conversation-Memory: Stateless persistence in PostgreSQL

2. **Technology Integration**:
   - Cohere Command model for NLP (temperature=0.1 for determinism)
   - Custom Cohere provider for OpenAI Agents SDK
   - SQLModel for all database operations
   - Pydantic for tool parameter validation

3. **Stateless Architecture**:
   - No in-memory conversation state
   - History retrieved from DB on every request
   - Context limited to last 20 messages (10 exchanges)
   - Supports horizontal scaling and fault tolerance

4. **Database Design**:
   - Conversations table (UUID PK, user_id FK)
   - Messages table (role, content, tool_calls JSONB)
   - Indexes on user_id, conversation_id, created_at
   - CASCADE deletes for referential integrity

5. **Frontend Architecture**:
   - Custom React components (no external chat library)
   - useChat hook for state management
   - Optimistic updates for responsive UX
   - Fixed chat icon + popup interface

**Constitution Check Results**:
- ✅ All 11 principles PASSED
- ✅ No violations or warnings
- ✅ Approved for Phase 0 Research
- ✅ All gates validated post-design

**File Structure**:
```
specs/001-ai-chatbot-integration/
├── spec.md                 (355 lines, 5 user stories, 20 requirements)
├── plan.md                 (350 lines, this planning doc)
├── research.md             (450 lines, 7 research topics)
├── data-model.md           (400 lines, 2 entities, 5 indexes)
├── quickstart.md           (500 lines, complete setup guide)
├── contracts/
│   ├── chat-api.yaml       (450 lines, OpenAPI 3.1.0)
│   └── mcp-tools.yaml      (150 lines, 5 tools)
└── checklists/
    └── requirements.md     (validation checklist, PASSED)
```

## Outcome

- ✅ Impact: Complete implementation plan created for Phase III AI Chatbot integration. Includes Technical Context, Constitution Check (11/11 passed), Phase 0 Research (7 topics), Phase 1 Design (data model, API contracts, quickstart guide). All planning artifacts validated and ready for task breakdown.
- 🧪 Tests: N/A (planning artifacts)
- 📁 Files: Created 6 files (plan.md, research.md, data-model.md, chat-api.yaml, mcp-tools.yaml, quickstart.md)
- 🔁 Next prompts:
  - `/sp.tasks` - Generate dependency-ordered task list for implementation
  - Review backend/src structure and verify compatibility with planned agents/ and services/ directories
  - Review frontend/src structure and verify ChatIcon can be added to global layout
  - Set up Cohere API account and obtain API key
  - Create database migrations for conversations and messages tables
- 🧠 Reflection: Planning phase successfully completed with comprehensive architecture design. Three-agent architecture provides clear separation of concerns. Cohere + Agents SDK integration well-researched with concrete implementation patterns. Stateless design enables horizontal scaling. Database schema supports user isolation and conversation persistence. All constitution principles validated with no violations. Ready for task breakdown and implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution Check PASSED 11/11 principles
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider adding agent prompt engineering examples to research.md for better intent classification accuracy (e.g., few-shot prompts for ambiguous commands like "finish that")
