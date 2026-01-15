---
id: 002
title: Update Constitution for Phase III AI Chatbot
stage: constitution
date: 2026-01-14
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: maryamkhanzada
command: /sp.constitution
labels: ["phase-iii", "ai-chatbot", "agents", "mcp", "cohere", "openai-agents-sdk", "constitution-update"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (constitution update, no tests required)
---

## Prompt

You are creating the FULL-CONSTITUTION prompt for Phase III of the Todo Full-Stack Web Application, integrating:

- Full backend (FastAPI + SQLModel + Neon PostgreSQL)
- Frontend (Next.js 16+ with Tailwind CSS, Better Auth + JWT)
- AI Todo Chatbot (OpenAI Agents SDK + Cohere API)

The constitution must define ALL rules, boundaries, conventions, and integration points for Claude Code or Spec-Kit Plus, including:

================================================================================
1️⃣ PROJECT SCOPE
================================================================================

- Full-stack web application with persistent storage
- Frontend already implemented with authentication, task management, and responsive design
- Backend implements RESTful API endpoints for tasks, authentication, and user management
- AI Todo Chatbot will:
    - Understand natural language instructions
    - Manage tasks via MCP tools (add, list, update, complete, delete)
    - Maintain stateless conversation with persistent memory (DB-backed)
    - Support multi-user isolation and JWT authentication

================================================================================
2️⃣ FOLDER STRUCTURE
================================================================================

/specs/features → Specifications for frontend, backend, chatbot, agents
/specs/agents  → Agent architecture and responsibilities
/skills        → Skills definitions for agents and frontend

- Frontend communicates with backend via authenticated REST API using JWT
- Chatbot frontend (ChatKit) calls: POST /api/{user_id}/chat with natural language input
- Backend handles: Request parsing, Agent orchestration, MCP tool execution, DB persistence for tasks and conversations
- Cohere API provides NLP embeddings, semantic search, and intent classification
- OpenAI Agents SDK executes logic for task operation decision-making

================================================================================
3️⃣ AGENT RULES
================================================================================

Define agents in backend:

1️⃣ Todo-Orchestrator Agent (Main Brain)
    - Receives user messages
    - Detects intent: add, list, update, complete, delete
    - Extracts entities: task_id, title, description, status
    - Decides MCP tool to invoke
    - Can chain multiple tools
    - Returns friendly, contextual responses

2️⃣ Task Operations Agent (MCP Executor)
    - Implements MCP tools: add_task, list_tasks, update_task, complete_task, delete_task
    - Enforces CRUD only for authenticated user
    - Performs SQLModel operations safely
    - Validates inputs and normalizes errors

3️⃣ Conversation Memory Agent (State Manager)
    - Persists chat history in DB (stateless server)
    - Maintains conversation_id
    - Tracks user & assistant messages
    - Supports conversation resumption and retrieval
    - Handles multi-session per user

================================================================================
4️⃣ INTEGRATION RULES
================================================================================

- Frontend sends JWT in Authorization header for all endpoints
- Chatbot frontend sends message + conversation_id to backend
- Backend:
    1. Validates JWT
    2. Fetches conversation history
    3. Passes user message + history to Todo-Orchestrator Agent
    4. Agent decides tool(s) and parameters
    5. Task Operations Agent executes MCP tools
    6. Conversation Memory Agent saves messages & responses
    7. Backend returns AI response + tool_calls to frontend
- Cohere API used by backend to: Classify intents, Extract entities, Embed task descriptions for semantic reasoning
- OpenAI Agents SDK logic runs on top of Cohere embeddings for tool decision-making

================================================================================
5️⃣ SECURITY RULES
================================================================================

- JWT tokens must never be hardcoded
- Backend must enforce ownership checks for all task operations
- Cohere API key must be stored in .env as COHERE_API_KEY
- OpenAI Agents SDK config must use environment variables for API credentials
- No user data should be exposed to other users
- Backend handles 401 Unauthorized, 403 Forbidden, and 404 Not Found consistently

================================================================================
6️⃣ DATABASE RULES
================================================================================

Tables:

1. users (managed by Better Auth)
   - id, email, name, created_at

2. tasks
   - id, user_id, title, description, completed, created_at, updated_at

3. conversations
   - id, user_id, created_at, updated_at

4. messages
   - id, user_id, conversation_id, role (user/assistant), content, created_at

Indexes:
- tasks.user_id
- tasks.completed
- messages.conversation_id

================================================================================
7️⃣ CODING CONVENTIONS
================================================================================

- Backend: Python 3.11+, FastAPI, SQLModel
- Frontend: Next.js 16+, TypeScript, Tailwind CSS
- Agents must use structured JSON for MCP tool calls
- Agent outputs must be deterministic
- Error messages must be user-friendly
- Conversation logs are persisted in DB (stateless server)
- All environment variables must be documented in README

================================================================================
8️⃣ CLAUDE CODE / SPEC-KIT PLUS INTEGRATION
================================================================================

- Root CLAUDE.md references: /specs/features/frontend-task-crud.md, /specs/features/frontend-auth.md, /specs/features/chatbot.md, /specs/features/chatbot-skills.md
- Backend CLAUDE.md includes instructions for: JWT verification, Agent orchestration, MCP tool execution, Cohere API usage
- Frontend CLAUDE.md includes instructions for: Sending JWT in API calls, Sending messages to /api/{user_id}/chat, Handling AI responses
- Spec-Kit Plus references: @specs/features/chatbot.md, @specs/agents/chatbot-agents.md, @specs/features/chatbot-skills.md

================================================================================
9️⃣ JUDGE-READY REQUIREMENTS
================================================================================

- All agents must operate **within defined skills**
- Chatbot must handle: add, list, update, complete, delete tasks via natural language, friendly confirmations, error handling (task not found, invalid input)
- Chatbot must support **stateless server** with persistent conversation memory
- Cohere API + OpenAI Agents SDK integration must work seamlessly
- System must be horizontally scalable
- Monorepo structure must allow Claude Code to modify frontend, backend, and agent logic in one context

================================================================================
DELIVERABLE
================================================================================

- Full-stack Todo App (frontend + backend + AI chatbot)
- REST API endpoints (FastAPI)
- MCP tools + Agent orchestration (OpenAI Agents SDK via Cohere)
- Persistent DB for tasks & conversations (Neon PostgreSQL)
- Frontend ChatKit integration
- Complete

## Response snapshot

Successfully updated constitution from version 1.0.0 to 1.1.0 with comprehensive Phase III AI Chatbot integration requirements.

**Version Change**: 1.0.0 → 1.1.0 (MINOR)

**Rationale**: Added four new principles (VIII-XI) for AI agent architecture, MCP tools, conversation memory, and AI/NLP integration. This is a material expansion that affects workflow but doesn't invalidate existing Phase II implementations - hence MINOR version bump.

**Key Additions**:
1. **Principle VIII: AI Agent Architecture** - Defines three agent roles (Todo-Orchestrator, Task-Ops-Executor, Conversation-Memory) with clear separation of concerns
2. **Principle IX: MCP Tools & Agent Orchestration** - Specifies contract-based interface for agent-data operations with 5 MCP tools
3. **Principle X: Conversation Memory & Stateless Architecture** - Mandates database-backed conversation state for horizontal scaling
4. **Principle XI: AI/NLP Integration** - Defines Cohere API and OpenAI Agents SDK usage patterns

**Modified Principles**:
- **Principle VII (Phase-Aware Implementation)**: Updated from Phase II to Phase III, added chatbot features to scope
- **Principle V (Tech Stack Enforcement)**: Added AI/NLP stack components (Cohere API, OpenAI Agents SDK, MCP Tools)
- **Principles I-IV**: Extended to include agent/chatbot requirements (spec requirements for agents, JWT validation for chatbot, chatbot endpoint patterns, conversation ownership)

**New Implementation Sections**:
- Agent Implementation Rules (Todo-Orchestrator, Task-Ops-Executor, Conversation-Memory)
- Chatbot Integration Rules (10-step request flow, response format, error handling)

**Updated Success Criteria**:
- Added 6 new categories: AI/Chatbot Functionality, Agent Architecture, External API Integration
- Extended existing categories for chatbot compatibility

**Template Compatibility**:
- ✅ plan-template.md - Constitution Check section supports new agent principles
- ✅ spec-template.md - Requirements format compatible with agent user stories
- ✅ tasks-template.md - Task organization supports agent implementation phases

## Outcome

- ✅ Impact: Constitution updated to version 1.1.0 with complete Phase III AI Chatbot integration requirements. All 11 principles clearly defined with rationales. Agent architecture, MCP tools, conversation memory, and AI/NLP integration fully specified.
- 🧪 Tests: N/A (constitution document - no executable tests required)
- 📁 Files: Updated 1 file (.specify/memory/constitution.md)
- 🔁 Next prompts:
  - Create agent specification documents in specs/agents/chatbot-agents.md
  - Create skills specification documents in specs/skills/chatbot-skills.md
  - Create API endpoints specification for chatbot in specs/api/rest-endpoints.md
  - Create database schema updates for conversations and messages tables
- 🧠 Reflection: Constitution now provides comprehensive guidance for Phase III development. Clear separation between Phase II (web app) and Phase III (AI chatbot) features. Agent architecture follows single-responsibility principle with MCP tools as security boundary. Stateless architecture enables horizontal scaling. All new principles include clear rationales and measurable compliance criteria.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (manual approval required for constitution amendments)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate constitution coverage by creating first agent spec document and checking for missing guidance or conflicts
