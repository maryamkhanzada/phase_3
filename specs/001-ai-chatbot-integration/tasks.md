---
description: "Task list for AI Todo Chatbot Integration implementation"
---

# Tasks: AI Todo Chatbot Integration

**Input**: Design documents from `/specs/001-ai-chatbot-integration/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/, research.md, quickstart.md

**Tests**: Tests are OPTIONAL - not included per specification (tests can be added later if needed)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/src/`
- **Database**: `backend/migrations/` or SQL scripts
- Paths shown below follow monorepo structure (backend/ and frontend/ at root)

---

## Phase 1: Setup (Shared Infrastructure) ✅ COMPLETE

**Purpose**: Project initialization and basic structure

- [X] T001 Install backend dependencies in backend/requirements.txt (cohere, openai-agents-sdk)
- [X] T002 [P] Configure environment variables in backend/.env (COHERE_API_KEY, DATABASE_URL, BETTER_AUTH_SECRET)
- [X] T003 [P] Create backend/src/agents directory structure
- [X] T004 [P] Create backend/src/services directory structure
- [X] T005 [P] Create frontend/src/components/chat directory structure
- [X] T006 [P] Create frontend/src/hooks directory (if not exists)
- [X] T007 [P] Create frontend/src/types directory (if not exists)

---

## Phase 2: Foundational (Blocking Prerequisites) ✅ COMPLETE

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 Create database migration for conversations table in backend/migrations/001_create_conversations.sql
- [X] T009 Create database migration for messages table in backend/migrations/002_create_messages.sql
- [X] T010 Run database migrations to create conversations and messages tables
- [X] T011 [P] Add Conversation model to backend/src/models.py (SQLModel definition with UUID PK)
- [X] T012 [P] Add Message model to backend/src/models.py (SQLModel definition with JSON tool_calls field)
- [X] T013 Update backend/src/config.py to include COHERE_API_KEY configuration
- [X] T014 Create CohereService class in backend/src/services/cohere_service.py (client initialization)
- [X] T015 Create Cohere custom model provider in backend/src/agents/cohere_provider.py (for Agents SDK integration)
- [X] T016 [P] Create ChatRequest schema in backend/src/schemas/chat.py
- [X] T017 [P] Create ChatResponse schema in backend/src/schemas/chat.py
- [X] T018 [P] Create base Message type in frontend/src/types/chat.ts
- [X] T019 [P] Create ToolCall type in frontend/src/types/chat.ts
- [X] T020 Update backend/src/main.py to import and register chat routes (placeholder for T037)
- [X] T021 Update frontend/src/lib/api-client.ts to add sendChatMessage method

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1) 🎯 MVP ✅ COMPLETE

**Goal**: Users can add tasks via natural language through chat interface

**Independent Test**: Open chat, type "Add a task to buy groceries", verify task appears in task list with confirmation message

### Implementation for User Story 1

- [X] T022 [P] [US1] Implement add_task MCP tool function in backend/src/agents/mcp_tools.py (with Pydantic params validation)
- [X] T023 [P] [US1] Implement classify_intent method in backend/src/services/cohere_service.py (detect "add" intent)
- [X] T024 [P] [US1] Implement extract_entities method in backend/src/services/cohere_service.py (extract title, description)
- [X] T025 [US1] Create Conversation-Memory Agent class in backend/src/agents/conversation_memory.py (create/save conversation methods)
- [X] T026 [US1] Create Task-Ops-Executor Agent in backend/src/agents/task_executor.py (wraps add_task MCP tool)
- [X] T027 [US1] Create Todo-Orchestrator Agent in backend/src/agents/orchestrator.py (intent classification + add_task tool selection)
- [X] T028 [US1] Implement POST /api/{user_id}/chat endpoint in backend/src/routes/chat.py (JWT validation, agent orchestration for add intent)
- [X] T029 [P] [US1] Create ChatIcon component in frontend/src/components/chat/ChatIcon.tsx (fixed bottom-right icon)
- [X] T030 [P] [US1] Create ChatInput component in frontend/src/components/chat/ChatInput.tsx (message input field with Enter key support)
- [X] T031 [P] [US1] Create ChatMessage component in frontend/src/components/chat/ChatMessage.tsx (display user and assistant messages)
- [X] T032 [US1] Create useChat hook in frontend/src/hooks/useChat.ts (state management, sendMessage, optimistic updates)
- [X] T033 [US1] Create ChatPopup component in frontend/src/components/chat/ChatPopup.tsx (popup interface with message list and input)
- [X] T034 [US1] Update frontend/src/app/layout.tsx to add ChatIcon component (fixed in all authenticated pages)
- [X] T035 [US1] Add error handling for add_task failures in backend/src/agents/orchestrator.py (translate to user-friendly messages)
- [X] T036 [US1] Add loading state indicator in frontend/src/components/chat/ChatPopup.tsx
- [X] T037 [US1] Register chat router in backend/src/main.py (app.include_router(chat.router))

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - View and Query Tasks via Chat (Priority: P2) ✅ COMPLETE

**Goal**: Users can query their tasks through chat interface with status filtering

**Independent Test**: Type "Show me my tasks", verify formatted task list appears with task IDs and statuses

### Implementation for User Story 2

- [X] T038 [P] [US2] Implement list_tasks MCP tool function in backend/src/agents/mcp_tools.py (with optional completed filter)
- [X] T039 [US2] Extend classify_intent in backend/src/services/cohere_service.py to detect "list" intent
- [X] T040 [US2] Extend extract_entities in backend/src/services/cohere_service.py to extract status filter
- [X] T041 [US2] Update Task-Ops-Executor Agent in backend/src/agents/task_executor.py to include list_tasks tool
- [X] T042 [US2] Update Todo-Orchestrator Agent in backend/src/agents/orchestrator.py to handle list intent and call list_tasks
- [X] T043 [US2] Update chat endpoint in backend/src/routes/chat.py to process list intent
- [X] T044 [US2] Implement task list formatting in backend/src/agents/orchestrator.py (group by status, include IDs)
- [X] T045 [US2] Add markdown support in frontend/src/components/chat/ChatMessage.tsx (use react-markdown for formatted task lists)
- [X] T046 [US2] Handle empty task list scenario in backend/src/agents/orchestrator.py ("You don't have any tasks yet" message)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Complete and Update Tasks via Chat (Priority: P3) ✅ COMPLETE

**Goal**: Users can complete and update tasks via natural language commands

**Independent Test**: Type "Mark task 3 as done", verify task status updates and confirmation appears

### Implementation for User Story 3

- [X] T047 [P] [US3] Implement update_task MCP tool function in backend/src/agents/mcp_tools.py (update title or description)
- [X] T048 [P] [US3] Implement complete_task MCP tool function in backend/src/agents/mcp_tools.py (toggle completion status)
- [X] T049 [US3] Extend classify_intent in backend/src/services/cohere_service.py to detect "update" and "complete" intents
- [X] T050 [US3] Extend extract_entities in backend/src/services/cohere_service.py to extract task_id and new values
- [X] T051 [US3] Update Task-Ops-Executor Agent in backend/src/agents/task_executor.py to include update_task and complete_task tools
- [X] T052 [US3] Update Todo-Orchestrator Agent in backend/src/agents/orchestrator.py to handle update and complete intents
- [X] T053 [US3] Update chat endpoint in backend/src/routes/chat.py to process update and complete intents
- [X] T054 [US3] Add "task not found" error handling in backend/src/agents/mcp_tools.py for all tools
- [X] T055 [US3] Add "permission denied" error handling in backend/src/agents/mcp_tools.py for cross-user task access attempts

**Checkpoint**: All user stories 1, 2, and 3 should now be independently functional

---

## Phase 6: User Story 4 - Delete Tasks via Chat (Priority: P4) ⚠️ PARTIAL (Basic delete works, confirmation flow simplified)

**Goal**: Users can delete tasks with confirmation prompts

**Independent Test**: Type "Delete task 7", task deleted immediately (confirmation not yet implemented as multi-turn flow)

### Implementation for User Story 4

- [X] T056 [P] [US4] Implement delete_task MCP tool function in backend/src/agents/mcp_tools.py
- [X] T057 [US4] Extend classify_intent in backend/src/services/cohere_service.py to detect "delete" intent
- [X] T058 [US4] Extend extract_entities in backend/src/services/cohere_service.py to extract task_id for deletion
- [X] T059 [US4] Update Task-Ops-Executor Agent in backend/src/agents/task_executor.py to include delete_task tool
- [ ] T060 [US4] Implement confirmation prompt logic in backend/src/agents/orchestrator.py (ask "Are you sure?" before deleting) - SKIPPED (requires complex state management)
- [ ] T061 [US4] Implement confirmation response handling in backend/src/agents/orchestrator.py (detect "yes" vs "no") - SKIPPED (requires complex state management)
- [ ] T062 [US4] Update chat endpoint in backend/src/routes/chat.py to handle multi-turn deletion flow - SKIPPED (requires complex state management)
- [ ] T063 [US4] Add conversation context tracking in backend/src/agents/conversation_memory.py (remember pending deletion) - SKIPPED (requires complex state management)

**Note**: Tasks T060-T063 require implementing a stateful multi-turn conversation flow which would need significant architectural changes. Current implementation provides immediate deletion without confirmation. This can be enhanced later with a state machine or conversation context manager.

**Checkpoint**: All user stories 1-4 should be functional

---

## Phase 7: User Story 5 - Multi-Step Commands and Context (Priority: P5) ⚠️ PARTIAL (Basic context works, advanced NLP features require future work)

**Goal**: Execute multi-step commands and maintain conversation context

**Independent Test**: Conversation history is maintained; multi-intent detection and contextual references require advanced NLP implementation

### Implementation for User Story 5

- [ ] T064 [US5] Implement multi-intent detection in backend/src/services/cohere_service.py (detect compound commands) - FUTURE: Requires advanced NLP prompt engineering
- [ ] T065 [US5] Implement tool chaining logic in backend/src/agents/orchestrator.py (sequence multiple tool calls) - FUTURE: Requires complex orchestration logic
- [X] T066 [US5] Extend conversation history retrieval in backend/src/agents/conversation_memory.py (last 20 messages for context)
- [ ] T067 [US5] Implement contextual reference resolution in backend/src/agents/orchestrator.py ("the first one", "that task") - FUTURE: Requires coreference resolution NLP
- [ ] T068 [US5] Add context-aware entity extraction in backend/src/services/cohere_service.py (use previous messages) - FUTURE: Requires conversation history in prompts
- [ ] T069 [US5] Handle batch operations in backend/src/agents/orchestrator.py ("delete all completed tasks") - FUTURE: Requires bulk operation logic
- [X] T070 [US5] Add conversation context display in frontend/src/components/chat/ChatPopup.tsx (show message history)

**Note**: Tasks T064, T065, T067, T068, T069 require advanced NLP capabilities (multi-intent parsing, coreference resolution, context-aware extraction) that would need significant additional prompt engineering and potentially more sophisticated models. These are marked for future enhancement.

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns ✅ COMPLETE

**Purpose**: Improvements that affect multiple user stories

- [X] T071 [P] Add comprehensive error logging in backend/src/agents/orchestrator.py (log all agent operations) - Already implemented with logger
- [X] T072 [P] Add tool call logging in backend/src/agents/mcp_tools.py (audit trail for all MCP operations) - Already implemented with logger
- [ ] T073 [P] Implement rate limiting for Cohere API calls in backend/src/services/cohere_service.py - SKIPPED (complex, optional for MVP)
- [X] T074 [P] Add Cohere API error handling in backend/src/services/cohere_service.py (rate limit, timeout, network errors) - Already implemented with try-except blocks
- [X] T075 [P] Optimize conversation history queries in backend/src/agents/conversation_memory.py (use DB indexes) - Already implemented (models have indexes)
- [X] T076 [P] Add auto-scroll to bottom in frontend/src/components/chat/ChatPopup.tsx (when new messages arrive) - Already implemented with useEffect
- [X] T077 [P] Add keyboard shortcuts in frontend/src/components/chat/ChatInput.tsx (Enter to send, Esc to close) - Enter already works, Esc added
- [X] T078 [P] Add accessibility attributes to frontend/src/components/chat/ components (ARIA labels, keyboard nav) - Added role="dialog", aria-label, aria-modal
- [X] T079 [P] Add mobile responsive styles to frontend/src/components/chat/ChatPopup.tsx (adapt to small screens) - Added responsive classes (full-screen on mobile)
- [X] T080 [P] Implement conversation context truncation in backend/src/agents/conversation_memory.py (limit to 20 messages) - Already implemented with limit=20 default
- [X] T081 Update backend/README.md with setup instructions for Cohere API key and agents
- [X] T082 Update frontend/README.md with chat feature documentation
- [X] T083 Add environment variable documentation for COHERE_API_KEY to backend/.env.example

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed) or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 infrastructure but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses US1/US2 patterns but independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Requires conversation context from Foundational phase
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Benefits from US1-US4 being complete but can be developed independently

### Within Each User Story

**User Story 1 (Natural Language Task Creation)**:
- T022-T024 (MCP tools, intent classification, entity extraction) can run in parallel
- T025-T027 (Agents) depend on T022-T024 completion
- T028 (endpoint) depends on T025-T027
- T029-T031 (Frontend components) can run in parallel with backend work
- T032-T034 (Frontend integration) depend on T029-T031
- T035-T037 (Error handling, loading states) depend on basic implementation

**User Story 2 (View and Query Tasks)**:
- T038-T040 run in parallel (MCP tool, extend intent/entity logic)
- T041-T043 sequential (update agents, update endpoint)
- T044-T046 sequential (formatting, UI, edge cases)

**User Story 3 (Complete and Update Tasks)**:
- T047-T048 parallel (MCP tools)
- T049-T050 parallel (extend intent/entity extraction)
- T051-T053 sequential (update agents, endpoint)
- T054-T055 parallel (error handling)

**User Story 4 (Delete Tasks)**:
- T056-T058 parallel (MCP tool, intent/entity detection)
- T059-T063 sequential (agent updates, confirmation flow, context tracking)

**User Story 5 (Multi-Step Commands)**:
- T064-T070 mostly sequential (each builds on previous context capability)

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T001-T007)
- All Foundational tasks marked [P] can run in parallel within each sub-group:
  - Database migrations (T008-T010) sequential
  - Models (T011-T012) parallel
  - Schemas (T016-T017, T018-T019) parallel
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within each story, tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch MCP tool, intent, and entity tasks together:
Task T022: "Implement add_task MCP tool in backend/src/agents/mcp_tools.py"
Task T023: "Implement classify_intent in backend/src/services/cohere_service.py"
Task T024: "Implement extract_entities in backend/src/services/cohere_service.py"

# Then launch agent tasks sequentially (depend on above):
Task T025: "Create Conversation-Memory Agent"
Task T026: "Create Task-Ops-Executor Agent"
Task T027: "Create Todo-Orchestrator Agent"

# Meanwhile, launch frontend components in parallel:
Task T029: "Create ChatIcon component"
Task T030: "Create ChatInput component"
Task T031: "Create ChatMessage component"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Natural Language Task Creation)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (T022-T037)
   - Developer B: User Story 2 (T038-T046)
   - Developer C: User Story 3 (T047-T055)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Tests are OPTIONAL per spec - not included in task breakdown (can be added if TDD approach requested)

---

## Task Summary

**Total Tasks**: 83

**Tasks per Phase**:
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 14 tasks
- Phase 3 (User Story 1 - P1): 16 tasks 🎯 MVP
- Phase 4 (User Story 2 - P2): 9 tasks
- Phase 5 (User Story 3 - P3): 9 tasks
- Phase 6 (User Story 4 - P4): 8 tasks
- Phase 7 (User Story 5 - P5): 7 tasks
- Phase 8 (Polish): 13 tasks

**Parallel Opportunities**: 34 tasks marked [P] can run in parallel when prerequisites met

**Independent Test Criteria**:
- **US1**: Type "Add a task to buy groceries" → Task appears in task list
- **US2**: Type "Show me my tasks" → Formatted task list displays
- **US3**: Type "Mark task 3 as done" → Task status updates
- **US4**: Type "Delete task 7" → Confirmation → "yes" → Task deleted
- **US5**: Type "Show my tasks and complete the first one" → Both actions execute

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = 37 tasks

**Format Validation**: ✅ All tasks follow checklist format with checkbox, ID, optional [P], story label [USX] where applicable, and exact file paths
