<!--
Sync Impact Report:
Version change: 1.0.0 → 1.1.0
Modified principles:
  - Phase-Aware Implementation: Updated from Phase II to Phase III (AI Chatbot integration)
  - Tech Stack Enforcement: Added AI/NLP components (Cohere API, OpenAI Agents SDK, MCP)
Added sections:
  - Principle VIII: AI Agent Architecture (NEW)
  - Principle IX: MCP Tools & Agent Orchestration (NEW)
  - Principle X: Conversation Memory & Stateless Architecture (NEW)
  - Principle XI: AI/NLP Integration (NEW)
  - Agent Implementation Rules (NEW)
  - Chatbot Integration Rules (NEW)
  - Database schema extended for conversations and messages
  - Security rules for API keys and chatbot-specific concerns
Templates requiring updates:
  ✅ plan-template.md - Constitution Check section covers new agent architecture principles
  ✅ spec-template.md - Requirements sections compatible with chatbot user stories
  ✅ tasks-template.md - Task organization supports agent and chatbot implementation phases
Follow-up TODOs: None
-->

# Todo Full-Stack Application with AI Chatbot - Constitution

## Core Principles

### I. Spec-First Development (MANDATORY)

Never implement anything without a written specification. All code must trace back to an approved spec document.

**Rules:**
- No feature implementation without a corresponding spec in `specs/<feature>/spec.md`
- All API endpoints must be documented in `specs/api/rest-endpoints.md` before implementation
- Database schema changes must be defined in `specs/database/schema.md` before migration
- Agent behaviors and skills must be documented in `specs/agents/` and `specs/skills/` before implementation
- Specs must be reviewed and approved before implementation begins
- Implementation must strictly match the spec - no undocumented behavior

**Rationale:** Spec-first development ensures clear requirements, enables independent review of design decisions before implementation cost is incurred, and creates living documentation that reflects system behavior. This prevents scope creep, reduces rework, and ensures all stakeholders understand what will be built.

### II. Authentication & Security (STRICT)

Authentication is JWT-based with strict user isolation enforced at all layers.

**Rules:**
- Better Auth runs ONLY on the frontend (Next.js)
- JWT tokens must be sent in `Authorization: Bearer <token>` header
- Backend MUST verify JWT signature using shared secret (BETTER_AUTH_SECRET)
- Backend MUST extract authenticated user_id from validated JWT token
- Backend MUST enforce user isolation on every data access request
- Never trust user_id from URL/request body - only from validated JWT
- Chatbot endpoints MUST validate JWT before processing messages
- Unauthenticated requests MUST return HTTP 401
- Unauthorized access attempts MUST return HTTP 403

**Rationale:** Security is non-negotiable. JWT-based authentication with server-side verification prevents token forgery and ensures only authenticated users access the system. User isolation prevents data leakage between accounts, which is critical for multi-tenant applications.

### III. API Design & RESTful Standards

All API endpoints follow REST conventions and live under `/api/` with consistent patterns.

**Rules:**
- All endpoints are RESTful and use appropriate HTTP verbs (GET, POST, PUT, DELETE)
- All endpoints require authentication unless explicitly documented as public
- Endpoints must follow pattern: `/api/<resource>` or `/api/<resource>/<id>`
- Chatbot endpoint follows pattern: `/api/{user_id}/chat` with POST method
- Response status codes must be semantically correct (200, 201, 400, 401, 403, 404, 500)
- Errors must return structured JSON with `{ "error": "message" }` format
- All endpoint contracts must be defined in `specs/api/rest-endpoints.md`
- Backend must handle CORS appropriately for frontend requests

**Rationale:** Consistent API design reduces cognitive load, makes the system predictable, and enables frontend developers to work independently once contracts are defined. REST conventions are widely understood and supported by tooling.

### IV. Data Ownership & User Isolation

Every data resource must be owned by a user, and users can only access their own data.

**Rules:**
- Every task record MUST include a `user_id` field
- Every conversation and message record MUST include a `user_id` field
- Every database query MUST filter by authenticated `user_id`
- No cross-user data leakage is allowed under any circumstances
- Task and conversation ownership must be enforced on all operations: Read, Create, Update, Delete
- Database constraints should enforce data ownership where possible
- All API responses must only include data owned by the authenticated user
- Chatbot must only access conversations and tasks belonging to the authenticated user

**Rationale:** User isolation is the foundation of data security in multi-tenant applications. Without strict enforcement at the data layer, authorization vulnerabilities can expose user data to unauthorized parties, violating user trust and potentially regulations (GDPR, CCPA, etc.).

### V. Tech Stack Enforcement

Technology choices are locked to ensure consistency and prevent fragmentation.

**Stack:**
- **Frontend:** Next.js 16+ (App Router), React Server Components, TypeScript, Tailwind CSS
- **Backend:** FastAPI (Python 3.11+), SQLModel for ORM
- **Database:** PostgreSQL (Neon hosted)
- **Authentication:** Better Auth (frontend only), JWT tokens
- **AI/NLP:** Cohere API (embeddings, intent classification, entity extraction)
- **Agent Framework:** OpenAI Agents SDK (tool orchestration, decision-making)
- **MCP Tools:** Custom MCP server for task operations (add, list, update, complete, delete)
- **Validation:** Pydantic models (backend), Zod schemas (frontend)
- **HTTP Client:** Centralized API client on frontend with automatic JWT attachment

**Rules:**
- Use Server Components by default; Client Components only when required (hooks, events, browser APIs)
- All backend database operations use SQLModel
- All API calls from frontend go through centralized API client
- JWT must be automatically attached to every authenticated request
- Use dependency injection or middleware for JWT verification on backend
- Cohere API must be used for all NLP tasks (intent classification, entity extraction, embeddings)
- OpenAI Agents SDK must orchestrate agent logic and tool selection
- MCP tools must be the ONLY interface for task database operations from agents

**Rationale:** Stack consistency reduces onboarding time, simplifies dependency management, and ensures team expertise is concentrated rather than fragmented across multiple technologies. These specific choices balance developer experience, performance, and ecosystem maturity.

### VI. Instruction Hierarchy

When instructions conflict, follow this priority order to resolve ambiguity.

**Priority Order (highest to lowest):**
1. **Spec documents** (`specs/<feature>/spec.md`, `specs/api/rest-endpoints.md`, `specs/agents/`, etc.)
2. **Root CLAUDE.md** (this file)
3. **Layer-specific CLAUDE.md** (`frontend/CLAUDE.md`, `backend/CLAUDE.md`)
4. **Constitution** (`.specify/memory/constitution.md`)
5. **Assumptions** (never assume - if not documented, ask for clarification)

**Load Order:**
1. Root `/CLAUDE.md`
2. Feature spec (e.g., `specs/features/chatbot.md`)
3. Agent spec (e.g., `specs/agents/chatbot-agents.md`)
4. Skills spec (e.g., `specs/skills/chatbot-skills.md`)
5. API spec (`specs/api/*`)
6. Database spec (`specs/database/*`)
7. UI spec (`specs/ui/*`)
8. Layer-specific CLAUDE.md files

**Rationale:** Clear hierarchy prevents decision paralysis when instructions conflict. Specs have highest priority because they represent explicit, reviewed requirements. CLAUDE.md provides workflow guidance. Constitution defines principles. Assumptions are forbidden to prevent undocumented behavior.

### VII. Phase-Aware Implementation

Implementation must respect the current project phase and avoid premature features.

**Current Phase:** Phase III – AI Todo Chatbot Integration

**Phase III Required Features:**
- All Phase II features (Task CRUD, Authentication, REST API, Persistent storage, Responsive UI)
- Natural language task management via AI chatbot
- Agent-based architecture (Todo-Orchestrator, Task-Ops-Executor, Conversation-Memory)
- MCP tools for task operations
- Conversation persistence and resumption (stateless server support)
- Cohere API integration for NLP (intent classification, entity extraction, embeddings)
- OpenAI Agents SDK integration for agent orchestration
- ChatKit frontend integration for conversational UI

**Explicitly Out of Scope:**
- Voice-based interactions
- Multi-language support beyond English
- Third-party integrations (Slack, email, calendar)
- Advanced analytics and reporting
- Real-time collaboration features
- Mobile native applications

**Rules:**
- Only implement features explicitly listed in current phase
- Future phase features must NOT be implemented unless explicitly requested and documented
- Phase transitions require updated specs and constitution amendments
- Avoid premature abstractions for future features
- Agent skills must be explicitly defined before implementation

**Rationale:** Phase discipline prevents over-engineering and keeps implementation focused on delivering current value. Building for speculative future requirements increases complexity, testing burden, and time to delivery without proven benefit.

### VIII. AI Agent Architecture (NEW)

Agents must follow a clear separation of concerns with defined responsibilities and communication patterns.

**Agent Roles:**
1. **Todo-Orchestrator Agent** (Main Brain): Receives user messages, detects intent, extracts entities, selects MCP tools, chains operations, generates responses
2. **Task-Ops-Executor Agent** (MCP Executor): Implements MCP tools, enforces CRUD with user isolation, performs SQLModel operations, validates inputs
3. **Conversation-Memory Agent** (State Manager): Persists chat history, maintains conversation_id, tracks messages, supports resumption

**Rules:**
- Agents must operate ONLY within their defined skills (see `specs/skills/`)
- Agents must NOT directly access the database - use MCP tools or service layers
- Todo-Orchestrator decides which MCP tools to invoke based on intent
- Task-Ops-Executor enforces user isolation on all database operations
- Conversation-Memory manages ALL conversation state (stateless server requirement)
- Agent outputs must be deterministic and reproducible
- Agents must use structured JSON for all MCP tool calls
- Error handling must translate technical errors into user-friendly messages

**Rationale:** Clear separation of concerns prevents agents from becoming monolithic and unmaintainable. Each agent has a single, well-defined responsibility that can be tested and evolved independently. MCP tools provide a contract-based interface that ensures user isolation and data integrity.

### IX. MCP Tools & Agent Orchestration (NEW)

MCP tools are the contract-based interface between agents and data operations.

**MCP Tools (Task Operations):**
- `add_task(user_id, title, description, completed)` → Creates new task
- `list_tasks(user_id, completed=None)` → Retrieves tasks with optional status filter
- `update_task(user_id, task_id, title=None, description=None)` → Updates task properties
- `complete_task(user_id, task_id, completed)` → Toggles task completion status
- `delete_task(user_id, task_id)` → Permanently deletes task

**Rules:**
- All MCP tools MUST enforce user_id validation (owner checks)
- MCP tools are the ONLY way agents interact with task data
- Tools must validate all inputs and return structured errors
- Tools must use SQLModel for all database operations
- Tool responses must be consistent JSON structures
- OpenAI Agents SDK orchestrates tool selection and execution
- Agents must handle tool errors gracefully and translate to user messages
- Tool calls must be logged for debugging and audit

**Rationale:** MCP tools create a security boundary that ensures user isolation is enforced consistently. Contract-based interfaces allow agents to be tested independently and prevent direct database access that could bypass security checks. Structured tool calls enable deterministic behavior and simplified debugging.

### X. Conversation Memory & Stateless Architecture (NEW)

Backend must be stateless with all conversation state persisted in the database.

**Rules:**
- Backend servers must NOT maintain in-memory conversation state
- Every conversation must have a unique `conversation_id`
- All user and assistant messages must be persisted in `messages` table
- Conversation history must be retrieved from database on every request
- Conversation-Memory Agent manages all persistence operations
- Support multiple concurrent conversations per user
- Enable conversation resumption after server restarts
- Conversation context must be limited to prevent excessive token usage
- Old conversations can be archived but not deleted (audit trail)

**Rationale:** Stateless architecture enables horizontal scaling and fault tolerance. Servers can be added/removed without losing conversation state. Persistent conversation memory ensures users can resume conversations after interruptions and provides an audit trail for debugging and compliance.

### XI. AI/NLP Integration (NEW)

Cohere API and OpenAI Agents SDK must be integrated for natural language understanding and agent orchestration.

**Cohere API Usage:**
- Intent classification (detect: add, list, update, complete, delete)
- Entity extraction (extract: task_id, title, description, status, priority)
- Semantic embeddings (for future task search and similarity)
- Text generation for user-friendly responses

**OpenAI Agents SDK Usage:**
- Agent logic orchestration (tool selection, parameter preparation)
- Multi-step workflow execution (tool chaining)
- Decision-making based on Cohere embeddings
- Structured output generation

**Rules:**
- Cohere API key must be stored in `.env` as `COHERE_API_KEY`
- OpenAI Agents SDK config must use environment variables for API credentials
- API keys must NEVER be hardcoded or committed to version control
- Use Cohere for all NLP tasks (don't duplicate with other services)
- OpenAI Agents SDK runs on top of Cohere embeddings for tool decisions
- Handle API rate limits and errors gracefully
- Cache embeddings where appropriate to reduce API costs
- Log all API calls for debugging and cost tracking

**Rationale:** Cohere provides state-of-the-art NLP capabilities for intent classification and entity extraction. OpenAI Agents SDK provides a robust framework for agent orchestration and tool selection. Using dedicated services for NLP avoids reinventing the wheel and ensures high-quality natural language understanding.

## Implementation Rules

### Frontend Rules

**Server Components (Default):**
- Use React Server Components by default for all pages and layouts
- Server Components enable direct data fetching, reduced client bundle, better SEO
- No `'use client'` directive unless hooks, event handlers, or browser APIs required

**Client Components (When Required):**
- Use `'use client'` directive for: useState, useEffect, event handlers, browser APIs
- Keep Client Components small and focused
- Prefer Server Components for data fetching and business logic

**API Integration:**
- All API calls MUST go through centralized API client (`lib/api-client.ts` or similar)
- JWT token MUST be automatically attached to every request
- Handle authentication errors (401) by redirecting to login
- Handle authorization errors (403) with appropriate user feedback
- Display loading states during API calls
- Handle and display API errors to users

**ChatKit Integration:**
- ChatKit component sends messages to `/api/{user_id}/chat` endpoint
- Include `conversation_id` in requests (generate new ID for first message)
- Display AI responses with proper formatting (markdown support)
- Show loading indicators while agent processes request
- Handle tool calls and display results contextually
- Support conversation history retrieval and display

### Backend Rules

**Database Operations:**
- Use SQLModel for all database models and queries
- All queries MUST filter by authenticated `user_id`
- Use async database operations where supported
- Handle database connection errors gracefully
- Enforce foreign key constraints for data integrity

**Validation:**
- Use Pydantic models for request/response validation
- Validate all input at API boundary
- Return 400 Bad Request for validation failures with clear error messages
- Validate user_id ownership on all data operations

**JWT Verification:**
- Use FastAPI dependency injection for JWT verification
- Create a dependency that validates JWT and extracts `user_id`
- Apply dependency to all protected endpoints (including chatbot)
- Handle JWT expiration, invalid signatures, missing tokens

**Error Handling:**
- Use appropriate HTTP status codes (400, 401, 403, 404, 500)
- Return structured JSON errors: `{ "error": "Human-readable message" }`
- Log errors server-side for debugging
- Never expose internal error details to clients
- Translate database errors into user-friendly messages

### Agent Implementation Rules

**Todo-Orchestrator Agent:**
- Receive user message and conversation history
- Use Cohere API to classify intent (add/list/update/complete/delete)
- Use Cohere API to extract entities (task_id, title, description, status)
- Decide which MCP tool(s) to invoke based on intent
- Prepare tool parameters from extracted entities
- Execute tools via OpenAI Agents SDK
- Generate friendly, contextual responses for users
- Handle multi-step workflows (e.g., "show my tasks and delete completed ones")
- Validate extracted entities before tool invocation

**Task-Ops-Executor Agent:**
- Implement all MCP tools (add_task, list_tasks, update_task, complete_task, delete_task)
- ALWAYS enforce user_id validation (verify ownership)
- Use SQLModel for all database operations
- Validate inputs (required fields, data types, constraints)
- Return structured responses with consistent format
- Translate database errors into user-friendly messages
- Log all operations for audit trail

**Conversation-Memory Agent:**
- Persist user messages with metadata (user_id, conversation_id, timestamp)
- Persist assistant messages with metadata (tool_calls, responses)
- Retrieve conversation history with pagination
- Manage conversation_id lifecycle (create, retrieve, archive)
- Support multiple concurrent conversations per user
- Prune old conversation context to manage token limits
- Handle database errors during persistence

### Chatbot Integration Rules

**Request Flow:**
1. Frontend sends POST to `/api/{user_id}/chat` with JWT + message + conversation_id
2. Backend validates JWT and extracts user_id
3. Backend retrieves conversation history from database (Conversation-Memory Agent)
4. Backend passes message + history to Todo-Orchestrator Agent
5. Todo-Orchestrator classifies intent and extracts entities (Cohere API)
6. Todo-Orchestrator decides tools and parameters (OpenAI Agents SDK)
7. Task-Ops-Executor executes MCP tools with user isolation
8. Conversation-Memory Agent saves user message and assistant response
9. Backend returns AI response + tool_calls to frontend
10. Frontend displays response and updates conversation UI

**Response Format:**
```json
{
  "message": "I've added 'Buy groceries' to your task list.",
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": { "title": "Buy groceries", "description": null, "completed": false },
      "result": { "id": 123, "title": "Buy groceries", "completed": false }
    }
  ],
  "conversation_id": "conv_abc123"
}
```

**Error Handling:**
- Invalid intents: "I'm not sure what you want to do. Try 'add task', 'show tasks', etc."
- Missing entities: "What should I name this task?"
- Task not found: "I couldn't find task #5. Please check the task number."
- Permission denied: "You don't have access to that task."
- System errors: "I'm having trouble right now. Please try again."

## Success Criteria

Implementation is considered successful when ALL of the following are met:

**Spec Compliance:**
- [ ] Code strictly matches approved specifications
- [ ] No undocumented behavior or features
- [ ] All API endpoints match `specs/api/rest-endpoints.md`
- [ ] Database schema matches `specs/database/schema.md`
- [ ] Agent behaviors match `specs/agents/chatbot-agents.md`
- [ ] Agent skills match `specs/skills/chatbot-skills.md`

**Authentication & Security:**
- [ ] All features require authentication (including chatbot)
- [ ] JWT verification works correctly
- [ ] User isolation is enforced on all data operations (tasks and conversations)
- [ ] No cross-user data leakage possible
- [ ] Unauthenticated requests return 401
- [ ] Unauthorized requests return 403
- [ ] API keys stored securely in environment variables

**Integration:**
- [ ] Frontend successfully communicates with backend
- [ ] JWT tokens automatically attached to requests
- [ ] ChatKit integration works correctly
- [ ] Authentication errors handled gracefully
- [ ] Loading and error states displayed to users

**Data Integrity:**
- [ ] All tasks associated with `user_id`
- [ ] All conversations and messages associated with `user_id`
- [ ] Users can only see/modify their own tasks and conversations
- [ ] Database constraints enforce ownership

**AI/Chatbot Functionality:**
- [ ] Chatbot understands natural language instructions
- [ ] Intent classification works accurately (add, list, update, complete, delete)
- [ ] Entity extraction captures required fields (task_id, title, description, status)
- [ ] MCP tools execute correctly with user isolation
- [ ] Tool chaining works for multi-step requests
- [ ] Responses are friendly and contextual
- [ ] Errors are translated to user-friendly messages
- [ ] Conversation history persists across sessions
- [ ] Stateless server supports horizontal scaling

**Agent Architecture:**
- [ ] Todo-Orchestrator Agent performs intent detection and tool selection
- [ ] Task-Ops-Executor Agent enforces user isolation on all operations
- [ ] Conversation-Memory Agent persists and retrieves conversation state
- [ ] Agents operate within defined skills
- [ ] Agent outputs are deterministic
- [ ] Tool calls use structured JSON

**External API Integration:**
- [ ] Cohere API integration works for intent classification
- [ ] Cohere API integration works for entity extraction
- [ ] OpenAI Agents SDK orchestrates tool selection
- [ ] API errors are handled gracefully
- [ ] API rate limits are respected

**Code Quality:**
- [ ] TypeScript types are correct and complete
- [ ] No type `any` without justification
- [ ] Error handling covers expected failure modes
- [ ] Logging implemented for debugging
- [ ] Agent code is testable and maintainable

**Documentation:**
- [ ] Specs exist and are up to date
- [ ] README explains how to run the application
- [ ] Environment variables documented (COHERE_API_KEY, OpenAI SDK config)
- [ ] API endpoints documented
- [ ] Agent architecture documented
- [ ] MCP tools documented

## Governance

### Constitution Authority

This constitution supersedes all other practices and guidelines. When conflicts arise, constitution principles take precedence after specs and CLAUDE.md hierarchy.

### Amendment Process

**Constitution amendments require:**
1. Documented rationale for the change
2. Impact assessment on existing specs and code
3. User/team approval
4. Version bump according to semantic versioning
5. Migration plan for affected artifacts
6. Update to this file with new `Last Amended` date

**Version Bumping Rules:**
- **MAJOR (X.0.0):** Backward incompatible changes, principle removals, or redefinitions that invalidate existing implementations
- **MINOR (0.X.0):** New principles added, material expansions to existing guidance that affect workflow
- **PATCH (0.0.X):** Clarifications, wording improvements, typo fixes, non-semantic refinements

### Compliance Review

**All development activities must verify compliance with:**
- Spec-first development (no implementation without spec)
- Authentication rules (JWT verification, user isolation for tasks and conversations)
- API design standards (REST conventions, error handling)
- Tech stack requirements (no unauthorized dependencies)
- Phase boundaries (no future-phase features)
- Agent architecture (separation of concerns, MCP tools, skills-based operation)
- Stateless server requirements (conversation persistence)

**Code reviews must check:**
- User isolation on all data queries (tasks, conversations, messages)
- JWT verification on all protected endpoints (including chatbot)
- Proper error handling and status codes
- Spec traceability for all features
- Agent skills compliance
- MCP tool usage for all task operations from agents
- Cohere API integration for NLP tasks
- Environment variable usage for API keys (no hardcoding)

**Complexity justification required when:**
- Adding new dependencies outside approved stack
- Introducing abstractions beyond current requirements
- Implementing features not in current phase
- Deviating from REST conventions
- Adding new agent roles beyond the three defined
- Creating direct database access from agents (bypass MCP tools)

### Runtime Guidance

For detailed runtime development guidance, refer to:
- `/CLAUDE.md` - Workflow and agent behavior
- `frontend/CLAUDE.md` - Frontend-specific guidance (if exists)
- `backend/CLAUDE.md` - Backend-specific guidance (if exists)
- `specs/agents/chatbot-agents.md` - Agent architecture and responsibilities
- `specs/skills/chatbot-skills.md` - Agent skills and capabilities

---

**Version**: 1.1.0 | **Ratified**: 2026-01-07 | **Last Amended**: 2026-01-14
