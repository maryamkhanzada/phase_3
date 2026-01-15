# Feature Specification: AI Todo Chatbot Integration

**Feature Branch**: `001-ai-chatbot-integration`
**Created**: 2026-01-14
**Status**: Draft
**Input**: User description: "Create a complete, full-stack specification for Phase III of the Todo Full-Stack Web Application, focusing on AI Todo Chatbot integration with Cohere API and OpenAI Agents SDK"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Task Creation (Priority: P1)

Users can add tasks to their todo list using natural, conversational language through a chat interface instead of filling out forms.

**Why this priority**: This is the core value proposition of the AI chatbot - allowing users to quickly capture tasks without context switching or form friction. It's the minimum viable chatbot feature.

**Independent Test**: Can be fully tested by opening the chat interface, typing "Add a task to buy groceries", and verifying the task appears in the task list with correct details. Delivers immediate value as a faster alternative to manual task creation.

**Acceptance Scenarios**:

1. **Given** user is authenticated and viewing any page, **When** user clicks the chat icon and types "Add a task to call the dentist", **Then** system creates a new task with title "call the dentist" and displays confirmation "I've added 'call the dentist' to your task list"

2. **Given** user is in the chat interface, **When** user types "Remind me to submit the report by Friday", **Then** system creates task with title "submit the report by Friday" and shows the task details in the chat response

3. **Given** user types "Create a task called 'Review code' with description 'Check PR #42 for security issues'", **When** system processes the message, **Then** task is created with title "Review code" and description "Check PR #42 for security issues"

4. **Given** user types ambiguous input like "Add milk", **When** system processes it, **Then** system creates task with title "Add milk" and asks "Would you like to add more details?"

---

### User Story 2 - View and Query Tasks via Chat (Priority: P2)

Users can ask the chatbot to show their tasks, filter by completion status, and get task summaries without navigating to the task list page.

**Why this priority**: Once users can create tasks via chat, they naturally want to retrieve them the same way. This completes the basic CRUD loop and makes the chatbot genuinely useful.

**Independent Test**: User can type "Show me my tasks" or "What do I need to do today?" and receive a formatted list of their pending tasks directly in the chat interface.

**Acceptance Scenarios**:

1. **Given** user has 3 pending tasks and 2 completed tasks, **When** user types "Show me my tasks", **Then** chatbot displays all 5 tasks grouped by status with task IDs, titles, and completion status

2. **Given** user has multiple tasks, **When** user types "What tasks are not done?", **Then** chatbot shows only pending tasks with their details

3. **Given** user types "List my completed tasks", **When** system processes the query, **Then** chatbot displays only completed tasks

4. **Given** user has no tasks, **When** user asks "Show my tasks", **Then** chatbot responds "You don't have any tasks yet. Want to add one?"

---

### User Story 3 - Complete and Update Tasks via Chat (Priority: P3)

Users can mark tasks as complete or update task details using natural language commands referencing task IDs or titles.

**Why this priority**: Builds on P1 and P2 to provide full task management through conversation. Less critical than creation and viewing, but completes the chatbot experience.

**Independent Test**: User can type "Mark task 3 as done" or "Complete 'buy groceries'" and verify the task status updates in both chat confirmation and task list.

**Acceptance Scenarios**:

1. **Given** user has a pending task with ID 5, **When** user types "Mark task 5 as complete", **Then** system updates the task status to completed and confirms "Task 5 'call the dentist' is now complete"

2. **Given** user has a task titled "Review code", **When** user types "Complete 'Review code'", **Then** system marks that task as done and displays confirmation

3. **Given** user has task ID 3 with title "Buy milk", **When** user types "Change task 3 title to 'Buy milk and bread'", **Then** system updates the title and confirms the change

4. **Given** user references a non-existent task ID, **When** user types "Complete task 999", **Then** chatbot responds "I couldn't find task #999. Please check the task number and try again"

---

### User Story 4 - Delete Tasks via Chat (Priority: P4)

Users can delete tasks using natural language commands with confirmation prompts to prevent accidental deletions.

**Why this priority**: Nice-to-have for completeness but not essential for MVP. Users can still delete from the web UI. Safety prompts add complexity.

**Independent Test**: User types "Delete task 7", receives a confirmation prompt "Are you sure you want to delete task 7 'submit report'?", confirms, and the task is removed.

**Acceptance Scenarios**:

1. **Given** user has task ID 7, **When** user types "Delete task 7", **Then** chatbot asks "Are you sure you want to delete task 7 'submit report'? (yes/no)"

2. **Given** chatbot asked for deletion confirmation, **When** user responds "yes", **Then** system deletes the task and confirms "Task 7 has been deleted"

3. **Given** chatbot asked for deletion confirmation, **When** user responds "no" or anything other than "yes", **Then** system cancels deletion and responds "Deletion cancelled. Task 7 is still in your list"

4. **Given** user tries to delete a non-existent task, **When** user types "Delete task 888", **Then** chatbot responds "I couldn't find task #888. Please check the task number"

---

### User Story 5 - Multi-Step Commands and Context (Priority: P5)

Users can execute multi-step commands in a single message and the chatbot maintains conversation context for follow-up queries.

**Why this priority**: Advanced feature that improves user experience but not required for basic functionality. Adds significant complexity to intent parsing and agent orchestration.

**Independent Test**: User types "Show my tasks and mark the first one as complete", chatbot displays tasks, identifies the first task, marks it complete, and confirms both actions.

**Acceptance Scenarios**:

1. **Given** user has multiple pending tasks, **When** user types "Show my tasks and complete the first one", **Then** chatbot lists tasks, identifies task with lowest ID, marks it complete, and confirms both actions

2. **Given** user just asked "Show my tasks", **When** user types "Complete the second one", **Then** chatbot uses context from previous response to identify and complete the second task from that list

3. **Given** chatbot just showed a task list, **When** user types "Delete all completed tasks", **Then** chatbot identifies completed tasks from recent context and asks for batch deletion confirmation

---

### Edge Cases

- What happens when user provides extremely long task titles or descriptions (>500 characters)?
- How does system handle rapid-fire messages before previous agent responses complete?
- What if Cohere API is temporarily unavailable or rate-limited?
- How does chatbot handle typos or misspelled commands ("shaw my tusks")?
- What happens when user switches between chat and web UI simultaneously (task list changes mid-conversation)?
- How does system handle conversation history after server restarts or deployments?
- What if user references task IDs that exist but belong to a different user?
- How does chatbot respond to completely unrelated queries ("What's the weather?")?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a persistent chat icon visible on all authenticated pages in the bottom-right corner
- **FR-002**: Chat icon MUST open a popup chat interface when clicked, overlaying the current page content
- **FR-003**: Chat interface MUST accept natural language text input from users
- **FR-004**: System MUST classify user intent from natural language (add, list, update, complete, delete tasks)
- **FR-005**: System MUST extract task entities from user messages (task_id, title, description, status)
- **FR-006**: System MUST validate JWT tokens on all chatbot API requests
- **FR-007**: System MUST enforce user isolation - users can only interact with their own tasks via chat
- **FR-008**: System MUST persist all conversation messages (user and assistant) in the database
- **FR-009**: System MUST retrieve conversation history on each request to maintain context
- **FR-010**: System MUST generate conversation IDs for new conversations and reuse existing IDs for continuations
- **FR-011**: System MUST support stateless backend servers - no in-memory conversation state
- **FR-012**: System MUST provide friendly, conversational responses to user inputs
- **FR-013**: System MUST confirm successful task operations with specific details (task ID, title, status)
- **FR-014**: System MUST translate technical errors into user-friendly messages
- **FR-015**: System MUST handle ambiguous inputs by making reasonable interpretations or asking clarifying questions
- **FR-016**: Chat interface MUST display conversation history (previous messages and responses)
- **FR-017**: Chat interface MUST show loading indicators while agent processes requests
- **FR-018**: Chat interface MUST support markdown formatting in assistant responses
- **FR-019**: System MUST limit conversation history context to prevent excessive token usage (reasonable default: last 20 messages or 10 exchanges)
- **FR-020**: System MUST log all agent operations and tool calls for debugging and audit

### Key Entities

- **Conversation**: Represents a chat session between a user and the AI chatbot. Contains conversation_id (unique identifier), user_id (owner), created_at timestamp, updated_at timestamp. Each user can have multiple concurrent conversations.

- **Message**: Represents a single message in a conversation. Contains message_id (unique identifier), conversation_id (parent conversation), user_id (owner), role (user or assistant), content (message text or response), tool_calls (JSON array of executed tools, nullable), created_at timestamp. Messages are ordered chronologically within a conversation.

- **Tool Call**: Embedded in Message entity. Represents an MCP tool execution. Contains tool_name (add_task, list_tasks, etc.), parameters (JSON object with tool inputs), result (JSON object with tool output), execution_status (success, error). Used for transparency and debugging.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task via chat in under 10 seconds from opening the chat interface to seeing confirmation
- **SC-002**: Chatbot correctly identifies user intent (add, list, update, complete, delete) with 90% accuracy on standard phrasing
- **SC-003**: Task operations initiated via chat complete successfully 95% of the time under normal conditions
- **SC-004**: Users receive responses from the chatbot within 3 seconds for simple queries (95th percentile)
- **SC-005**: Conversation history persists across server restarts and users can resume conversations seamlessly
- **SC-006**: System supports at least 100 concurrent chat conversations without degradation
- **SC-007**: Zero cross-user data leakage - all task operations via chat are correctly isolated by authenticated user
- **SC-008**: Chat interface is accessible and functional on desktop and mobile screen sizes
- **SC-009**: Error messages are human-readable and actionable 100% of the time (no raw error dumps)
- **SC-010**: Chatbot handles multi-step commands (e.g., "show tasks and complete the first one") successfully 80% of the time

## Assumptions

1. **Natural Language Patterns**: Users will primarily use common English phrasing patterns for task management. Cohere's pre-trained models provide adequate intent classification for standard commands without custom training.

2. **Conversation Scope**: Each conversation session remains focused on task management. Users won't expect the chatbot to handle unrelated queries (weather, general knowledge, etc.). Out-of-scope queries receive polite redirection.

3. **Response Time Expectations**: Users accept 2-3 second response times for chat interactions, comparable to other AI chatbot experiences. Longer delays for complex multi-step operations are acceptable with loading indicators.

4. **Context Window**: Maintaining last 20 messages (10 exchanges) provides sufficient context for most conversations while keeping token costs reasonable. Older context can be summarized or truncated.

5. **Task Identification**: When users reference tasks by title (e.g., "complete 'buy groceries'"), exact string matching is sufficient. Fuzzy matching or semantic search for task titles is out of scope for Phase III.

6. **Conversation Isolation**: Each conversation is independent. Users don't expect cross-conversation context (e.g., "delete the task from yesterday's chat"). Context is limited to the current conversation.

7. **Error Recovery**: When Cohere API is unavailable, chatbot can gracefully degrade by showing a status message. Implementing a fallback NLP service is out of scope.

8. **Agent Handoffs**: OpenAI Agents SDK with Cohere integration handles agent orchestration reliably. Custom handoff logic beyond SDK capabilities is not required.

9. **Conversation Retention**: Conversations persist indefinitely for audit and context purposes. Automatic archival or deletion of old conversations is out of scope.

10. **UI Framework**: Frontend team can implement the chat interface using existing Next.js and Tailwind CSS patterns. No specialized chat UI library is required, though one may be used if available (e.g., ChatKit).

## Dependencies

- **External Services**: Cohere API for natural language processing (intent classification, entity extraction, embeddings). System cannot function without Cohere API access.

- **Existing Backend**: RESTful task management API endpoints (`/api/tasks/*`) must be operational with JWT authentication enforced.

- **Existing Frontend**: User authentication via Better Auth and JWT token management must be working. Chat interface integrates into existing authenticated layout.

- **Database**: Neon PostgreSQL database must have `conversations` and `messages` tables created before chatbot deployment.

- **OpenAI Agents SDK**: Backend must have Agents SDK installed and configured to use Cohere as the model provider instead of default Gemini/OpenAI models.

## Out of Scope

- Voice-based interactions or speech-to-text input
- Multi-language support beyond English
- Real-time typing indicators or "agent is thinking" animations beyond basic loading state
- Task recommendations or smart suggestions based on user behavior
- Integration with external calendar, email, or productivity tools
- Shared conversations or collaborative task management via chat
- Custom training or fine-tuning of Cohere models
- Advanced analytics on conversation patterns or chatbot performance metrics
- Conversation export or sharing functionality
- Task scheduling or reminder notifications triggered by chat commands
- Conversation search across all user conversations

## Security and Privacy Considerations

1. **Authentication**: All chatbot API endpoints require valid JWT tokens. Unauthenticated requests return HTTP 401.

2. **User Isolation**: Conversation and task data are strictly isolated by `user_id` extracted from validated JWT. Agent operations enforce ownership checks at the database layer.

3. **API Key Protection**: Cohere API key stored in backend `.env` file as `COHERE_API_KEY`. Never exposed to frontend or logged.

4. **Input Sanitization**: All user messages sanitized before processing to prevent injection attacks. Chatbot responses escaped before rendering in frontend to prevent XSS.

5. **Data Retention**: Conversation history contains user task data. Conversations persist in database and are subject to same security controls as task data.

6. **Rate Limiting**: Consider implementing per-user rate limits on chat API to prevent abuse of Cohere API quota (recommendation: 100 messages per hour per user).

7. **Error Disclosure**: Error messages to users never expose internal system details, stack traces, or database schema information.

8. **Audit Trail**: All tool calls logged with user_id, timestamp, tool_name, parameters, and result for security auditing and debugging.

## Technical Constraints

1. **Stateless Backend**: Backend servers maintain no in-memory conversation state. All context retrieved from database on each request to support horizontal scaling.

2. **Token Limits**: Cohere API has token limits per request. Conversation history must be truncated or summarized to stay within limits (default strategy: last 20 messages).

3. **Response Time**: Cohere API calls add latency. Target 95th percentile response time of 3 seconds requires efficient context retrieval and minimal API round-trips.

4. **Database Constraints**: `conversations` and `messages` tables must have indexes on `user_id` and `conversation_id` for performant history queries.

5. **Agent SDK Integration**: OpenAI Agents SDK typically uses Gemini/OpenAI models. Integrating Cohere requires custom configuration to replace the default model provider.

6. **MCP Tool Interface**: Task operations agent must expose MCP-compliant tools that Agents SDK can invoke. Tool definitions must follow MCP schema conventions.

7. **Frontend State**: Chat interface must manage local state for real-time message display while backend persists to database asynchronously. Optimistic UI updates recommended.

8. **CORS Configuration**: Backend must allow CORS requests from frontend origin for chat API endpoints.

## Interface Contracts

### Chat API Endpoint

**Endpoint**: `POST /api/{user_id}/chat`

**Request Headers**:
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Request Body**:
```json
{
  "conversation_id": "conv_abc123",  // Optional for first message, required for continuations
  "message": "Add a task to buy groceries"
}
```

**Success Response** (HTTP 200):
```json
{
  "conversation_id": "conv_abc123",
  "message": "I've added 'buy groceries' to your task list.",
  "tool_calls": [
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
        "created_at": "2026-01-14T20:00:00Z"
      }
    }
  ],
  "timestamp": "2026-01-14T20:00:01Z"
}
```

**Error Responses**:

- **HTTP 401**: Invalid or missing JWT token
  ```json
  {
    "error": "Authentication required. Please log in."
  }
  ```

- **HTTP 403**: User ID in URL doesn't match JWT
  ```json
  {
    "error": "You don't have permission to access this conversation."
  }
  ```

- **HTTP 400**: Invalid request format
  ```json
  {
    "error": "Message text is required."
  }
  ```

- **HTTP 500**: Internal server error
  ```json
  {
    "error": "I'm having trouble right now. Please try again in a moment."
  }
  ```

### MCP Tools Contract

**Tool: add_task**
- **Parameters**: `user_id` (string), `title` (string), `description` (string, optional), `completed` (boolean, default false)
- **Returns**: Created task object with id, user_id, title, description, completed, created_at, updated_at
- **Errors**: ValidationError if title empty, PermissionError if user_id invalid

**Tool: list_tasks**
- **Parameters**: `user_id` (string), `completed` (boolean, optional filter)
- **Returns**: Array of task objects matching filter
- **Errors**: PermissionError if user_id invalid

**Tool: update_task**
- **Parameters**: `user_id` (string), `task_id` (integer), `title` (string, optional), `description` (string, optional)
- **Returns**: Updated task object
- **Errors**: NotFoundError if task doesn't exist, PermissionError if task belongs to different user

**Tool: complete_task**
- **Parameters**: `user_id` (string), `task_id` (integer), `completed` (boolean)
- **Returns**: Updated task object with new completion status
- **Errors**: NotFoundError if task doesn't exist, PermissionError if task belongs to different user

**Tool: delete_task**
- **Parameters**: `user_id` (string), `task_id` (integer)
- **Returns**: Success confirmation with deleted task_id
- **Errors**: NotFoundError if task doesn't exist, PermissionError if task belongs to different user
