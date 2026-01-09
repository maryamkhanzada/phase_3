# Feature Specification: Backend REST API for Todo Application

**Feature Branch**: `002-backend-api`
**Created**: 2026-01-09
**Status**: Draft
**Input**: User description: "Create a complete, production-ready backend specification for Phase II of the Todo Full-Stack Web Application and ensure full integration compatibility with the already specified frontend."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - JWT Token Authentication and Validation (Priority: P1)

The backend must authenticate every incoming request using JWT tokens issued by Better Auth, extract the authenticated user's identity, and enforce strict data isolation to ensure users can only access their own resources.

**Why this priority**: Authentication is the foundation of security and data isolation. Without proper JWT validation, the entire system is vulnerable and users could access each other's data. This is the critical first layer that protects all subsequent operations.

**Independent Test**: Can be fully tested by sending requests with valid tokens (200 OK), invalid tokens (401), expired tokens (401), and missing tokens (401). Delivers secure request authentication.

**Acceptance Scenarios**:

1. **Given** a request to any protected endpoint with a valid JWT token in the Authorization header, **When** the backend validates the token signature using BETTER_AUTH_SECRET, **Then** the request proceeds and user_id is extracted from the JWT payload for data filtering.

2. **Given** a request to any protected endpoint with an invalid JWT signature, **When** the backend attempts to validate the token, **Then** the backend returns 401 Unauthorized with `{"error": "Unauthorized"}`.

3. **Given** a request to any protected endpoint with an expired JWT token, **When** the backend checks the token expiration claim, **Then** the backend returns 401 Unauthorized with `{"error": "Unauthorized"}`.

4. **Given** a request to any protected endpoint without an Authorization header, **When** the backend checks for authentication, **Then** the backend returns 401 Unauthorized with `{"error": "Unauthorized"}`.

5. **Given** a request to any protected endpoint with a malformed Authorization header (e.g., missing "Bearer" prefix), **When** the backend parses the header, **Then** the backend returns 401 Unauthorized with `{"error": "Unauthorized"}`.

---

### User Story 2 - User Registration and Login (Priority: P2)

The backend must provide signup and login endpoints that create new user accounts, authenticate existing users, and issue JWT tokens for session management.

**Why this priority**: After authentication infrastructure is in place, users need actual endpoints to obtain tokens. This enables frontend authentication flows and is the gateway to all task management features.

**Independent Test**: Can be fully tested by submitting signup requests with valid credentials (201), invalid credentials (400), duplicate emails (409), and login requests with correct/incorrect credentials. Delivers user account creation and authentication.

**Acceptance Scenarios**:

1. **Given** a POST request to /api/auth/signup with valid email and password (≥8 characters), **When** the backend validates the input and creates the user account, **Then** the backend returns 201 Created with `{"token": "<jwt>", "user": {"id": "<uuid>", "email": "<email>"}}`.

2. **Given** a POST request to /api/auth/signup with an email that already exists in the database, **When** the backend checks for existing users, **Then** the backend returns 409 Conflict with `{"error": "Email already registered"}`.

3. **Given** a POST request to /api/auth/signup with invalid email format or password shorter than 8 characters, **When** the backend validates the input, **Then** the backend returns 400 Bad Request with `{"error": "<validation message>"}`.

4. **Given** a POST request to /api/auth/login with valid credentials matching an existing user, **When** the backend authenticates the credentials, **Then** the backend returns 200 OK with `{"token": "<jwt>", "user": {"id": "<uuid>", "email": "<email>"}}`.

5. **Given** a POST request to /api/auth/login with incorrect email or password, **When** the backend attempts authentication, **Then** the backend returns 401 Unauthorized with `{"error": "Invalid email or password"}`.

---

### User Story 3 - Fetch User's Task List with Strict Isolation (Priority: P3)

The backend must retrieve all tasks belonging to the authenticated user and ONLY the authenticated user, enforcing strict data isolation at the database query level.

**Why this priority**: After authentication is working, users need to retrieve their task data. This is the first read operation that delivers actual business value and proves data isolation is enforced.

**Independent Test**: Can be fully tested by authenticating as User A, fetching tasks, verifying only User A's tasks are returned, then authenticating as User B and verifying different tasks. Delivers secure task retrieval.

**Acceptance Scenarios**:

1. **Given** an authenticated user with 5 tasks in the database, **When** they send GET /api/tasks with a valid JWT token, **Then** the backend returns 200 OK with `{"tasks": [<array of 5 tasks>]}` filtered by user_id from the JWT.

2. **Given** an authenticated user with no tasks in the database, **When** they send GET /api/tasks with a valid JWT token, **Then** the backend returns 200 OK with `{"tasks": []}`.

3. **Given** an authenticated user, **When** another user's tasks exist in the database, **Then** the GET /api/tasks response contains ONLY the authenticated user's tasks (user_id from JWT matches task.user_id).

4. **Given** an unauthenticated request to GET /api/tasks without an Authorization header, **When** the backend checks authentication, **Then** the backend returns 401 Unauthorized with `{"error": "Unauthorized"}`.

---

### User Story 4 - Create New Task with Automatic User Assignment (Priority: P4)

The backend must create new tasks and automatically assign them to the authenticated user based on the JWT token, never trusting client-provided user_id values.

**Why this priority**: Task creation is essential for users to add content to their lists. This builds on authentication and read operations to enable the first write capability.

**Independent Test**: Can be fully tested by authenticating, creating a task, verifying it's assigned to the correct user_id, and confirming another user cannot see it. Delivers secure task creation.

**Acceptance Scenarios**:

1. **Given** an authenticated user sending POST /api/tasks with `{"title": "Buy groceries", "description": "Milk, eggs"}` and a valid JWT token, **When** the backend creates the task, **Then** the backend returns 201 Created with `{"task": {...}}` where task.user_id equals the user_id from the JWT (not from request body).

2. **Given** an authenticated user sending POST /api/tasks with `{"title": "Task title"}` (no description) and a valid JWT token, **When** the backend creates the task, **Then** the backend returns 201 Created with description set to null.

3. **Given** an authenticated user sending POST /api/tasks with `{"description": "No title"}` (missing required title), **When** the backend validates the request, **Then** the backend returns 400 Bad Request with `{"error": "Title is required"}`.

4. **Given** an authenticated user sending POST /api/tasks with `{"title": ""}` (empty title), **When** the backend validates the request, **Then** the backend returns 400 Bad Request with `{"error": "Title is required"}`.

5. **Given** an unauthenticated request to POST /api/tasks, **When** the backend checks authentication, **Then** the backend returns 401 Unauthorized with `{"error": "Unauthorized"}`.

---

### User Story 5 - Update Task with Authorization Enforcement (Priority: P5)

The backend must allow users to update their own tasks (title, description, completion status) while preventing unauthorized access to tasks owned by other users.

**Why this priority**: Task updates enhance user experience by allowing corrections and status changes. This is important but not critical for initial MVP since users can delete and recreate tasks.

**Independent Test**: Can be fully tested by creating a task as User A, updating it successfully, then attempting to update it as User B and verifying 403 Forbidden. Delivers secure task modification.

**Acceptance Scenarios**:

1. **Given** an authenticated user owning task ID "task-123", **When** they send PUT /api/tasks/task-123 with `{"title": "Updated title", "completed": true}` and a valid JWT token, **Then** the backend returns 200 OK with the updated task where updated_at timestamp is newer than created_at.

2. **Given** an authenticated user attempting to update task ID "task-456" owned by a different user, **When** the backend checks task ownership against the JWT user_id, **Then** the backend returns 403 Forbidden with `{"error": "Access denied"}`.

3. **Given** an authenticated user sending PUT /api/tasks/task-123 with `{"title": ""}` (empty title), **When** the backend validates the input, **Then** the backend returns 400 Bad Request with `{"error": "Title cannot be empty"}`.

4. **Given** an authenticated user sending PUT /api/tasks/nonexistent-id, **When** the backend queries the database, **Then** the backend returns 404 Not Found with `{"error": "Task not found"}`.

5. **Given** an authenticated user sending PUT /api/tasks/task-123 with `{"completed": true}` only (partial update), **When** the backend applies the update, **Then** the backend returns 200 OK with only the completed field changed, preserving title and description.

---

### User Story 6 - Delete Task with Authorization Enforcement (Priority: P6)

The backend must allow users to permanently delete their own tasks while preventing deletion of tasks owned by other users.

**Why this priority**: Task deletion is essential for list maintenance but is the lowest priority CRUD operation. Users can simply ignore unwanted tasks temporarily if this feature is delayed.

**Independent Test**: Can be fully tested by creating a task, deleting it successfully (204), verifying it no longer exists (404 on GET), and attempting to delete another user's task (403). Delivers secure task removal.

**Acceptance Scenarios**:

1. **Given** an authenticated user owning task ID "task-789", **When** they send DELETE /api/tasks/task-789 with a valid JWT token, **Then** the backend deletes the task from the database and returns 204 No Content (empty response body).

2. **Given** an authenticated user attempting to delete task ID "task-999" owned by a different user, **When** the backend checks task ownership against the JWT user_id, **Then** the backend returns 403 Forbidden with `{"error": "Access denied"}`.

3. **Given** an authenticated user sending DELETE /api/tasks/nonexistent-id, **When** the backend queries the database, **Then** the backend returns 404 Not Found with `{"error": "Task not found"}`.

4. **Given** an authenticated user who previously deleted task ID "task-789", **When** they attempt to delete the same task again, **Then** the backend returns 404 Not Found with `{"error": "Task not found"}`.

---

### Edge Cases

- **Concurrent task updates from multiple sessions**: When a user edits the same task in two browser tabs simultaneously, the last write wins. The backend updates the task based on the most recent PUT request, potentially overwriting changes from the first request. No optimistic locking or conflict detection is required in Phase II.

- **Task ownership changes**: When a task's user_id is manually changed in the database (e.g., via admin tool), the original owner can no longer access it via API. The backend MUST always filter by JWT user_id, preventing unauthorized access even if the database is modified externally.

- **JWT token with missing user_id claim**: When a JWT token is structurally valid but missing the required user_id claim in the payload, the backend returns 401 Unauthorized and logs the malformed token event for security monitoring.

- **Database connection failure during request**: When the database is unreachable or times out during a request, the backend returns 500 Internal Server Error with `{"error": "Service temporarily unavailable"}` and logs the database error for operations team investigation.

- **Request body exceeds size limit**: When a request body exceeds the configured maximum size (e.g., 1MB), FastAPI automatically returns 413 Request Entity Too Large before the request reaches handler code.

- **Invalid JSON in request body**: When a request contains malformed JSON, FastAPI returns 422 Unprocessable Entity with validation error details.

- **SQL injection attempts**: When a request contains SQL injection payloads in title or description fields, SQLModel's parameterized queries prevent injection, treating the input as literal text. The backend sanitizes input via Pydantic validation, stripping dangerous characters if necessary.

- **User deletion with existing tasks**: When a user account is deleted (out of scope for Phase II but future consideration), all associated tasks SHOULD be cascade deleted via foreign key constraint to prevent orphaned data.

- **Very long task titles or descriptions**: When a user submits a title exceeding 255 characters or description exceeding 1000 characters, Pydantic validation truncates or rejects the input with 400 Bad Request before database insertion.

- **Token signature algorithm mismatch**: When a JWT token uses a different signing algorithm than expected (e.g., RS256 instead of HS256), signature verification fails and the backend returns 401 Unauthorized.

## Requirements *(mandatory)*

### Functional Requirements

**Authentication & Token Validation:**

- **FR-001**: System MUST extract JWT tokens from the Authorization header in format "Bearer <token>".
- **FR-002**: System MUST validate JWT signature using BETTER_AUTH_SECRET environment variable as the shared secret.
- **FR-003**: System MUST verify JWT token expiration claim (exp) and reject expired tokens with 401 Unauthorized.
- **FR-004**: System MUST extract user_id from the JWT payload (subject or user_id claim) for all authenticated operations.
- **FR-005**: System MUST return 401 Unauthorized for any protected endpoint when token is missing, invalid, malformed, or expired.
- **FR-006**: System MUST provide a reusable FastAPI dependency (e.g., `get_current_user`) that performs JWT validation and returns the authenticated user_id.

**User Registration & Login:**

- **FR-007**: System MUST provide POST /api/auth/signup endpoint accepting `{"email": string, "password": string}` in request body.
- **FR-008**: System MUST validate email format (RFC 5322 compliant) and password length (minimum 8 characters) for signup requests.
- **FR-009**: System MUST check for existing users by email before creating a new account and return 409 Conflict if email is already registered.
- **FR-010**: System MUST hash passwords using a secure algorithm (e.g., bcrypt with appropriate cost factor) before storing in the database.
- **FR-011**: System MUST generate a JWT token containing user_id and email claims with appropriate expiration (e.g., 24 hours) upon successful signup.
- **FR-012**: System MUST return 201 Created with `{"token": string, "user": {"id": string, "email": string}}` after successful signup.
- **FR-013**: System MUST provide POST /api/auth/login endpoint accepting `{"email": string, "password": string}` in request body.
- **FR-014**: System MUST verify email exists and password matches the stored hash for login requests.
- **FR-015**: System MUST return 401 Unauthorized with `{"error": "Invalid email or password"}` for failed login attempts.
- **FR-016**: System MUST generate a JWT token with the same structure and expiration as signup upon successful login.
- **FR-017**: System MUST return 200 OK with `{"token": string, "user": {"id": string, "email": string}}` after successful login.

**Task Retrieval:**

- **FR-018**: System MUST provide GET /api/tasks endpoint that requires authentication via JWT token.
- **FR-019**: System MUST filter tasks by user_id extracted from the JWT token (never accept user_id from query parameters or request body).
- **FR-020**: System MUST return 200 OK with `{"tasks": [array of task objects]}` where each task includes id, title, description, completed, user_id, created_at, updated_at.
- **FR-021**: System MUST return an empty array `{"tasks": []}` when the authenticated user has no tasks.
- **FR-022**: System MUST order tasks by created_at descending (newest first) by default.

**Task Creation:**

- **FR-023**: System MUST provide POST /api/tasks endpoint that requires authentication via JWT token.
- **FR-024**: System MUST accept request body with `{"title": string (required), "description": string | null (optional)}`.
- **FR-025**: System MUST validate title is non-empty (after trimming whitespace) and return 400 Bad Request if validation fails.
- **FR-026**: System MUST automatically set user_id to the authenticated user's ID from the JWT token (never trust client-provided user_id).
- **FR-027**: System MUST automatically set completed to false, created_at to current UTC timestamp, and updated_at to current UTC timestamp.
- **FR-028**: System MUST generate a unique UUID for the task ID (version 4).
- **FR-029**: System MUST return 201 Created with `{"task": {<full task object>}}` after successful creation.

**Task Updates:**

- **FR-030**: System MUST provide PUT /api/tasks/:id endpoint that requires authentication via JWT token.
- **FR-031**: System MUST accept request body with optional fields: `{"title": string, "description": string | null, "completed": boolean}`.
- **FR-032**: System MUST verify the task with the given ID exists and return 404 Not Found if it does not.
- **FR-033**: System MUST verify the task belongs to the authenticated user (task.user_id == JWT user_id) and return 403 Forbidden if ownership check fails.
- **FR-034**: System MUST validate that if title is provided, it is non-empty, and return 400 Bad Request if validation fails.
- **FR-035**: System MUST update only the fields provided in the request body (partial updates allowed).
- **FR-036**: System MUST automatically update the updated_at timestamp to the current UTC time on every update.
- **FR-037**: System MUST return 200 OK with `{"task": {<full updated task object>}}` after successful update.

**Task Deletion:**

- **FR-038**: System MUST provide DELETE /api/tasks/:id endpoint that requires authentication via JWT token.
- **FR-039**: System MUST verify the task with the given ID exists and return 404 Not Found if it does not.
- **FR-040**: System MUST verify the task belongs to the authenticated user (task.user_id == JWT user_id) and return 403 Forbidden if ownership check fails.
- **FR-041**: System MUST permanently delete the task from the database.
- **FR-042**: System MUST return 204 No Content (empty response body) after successful deletion.

**Database & Data Integrity:**

- **FR-043**: System MUST use SQLModel ORM for all database operations (no raw SQL queries except for complex operations not supported by ORM).
- **FR-044**: System MUST define a Task model with fields: id (UUID primary key), title (String, max 255 chars, non-nullable), description (Text, nullable), completed (Boolean, default false), user_id (UUID, foreign key to users table), created_at (DateTime, auto-set), updated_at (DateTime, auto-updated).
- **FR-045**: System MUST define a User model with fields: id (UUID primary key), email (String, unique, non-nullable), password_hash (String, non-nullable), created_at (DateTime, auto-set).
- **FR-046**: System MUST create a foreign key relationship from Task.user_id to User.id with appropriate constraints.
- **FR-047**: System MUST create an index on Task.user_id for efficient query filtering.
- **FR-048**: System MUST use Neon Serverless PostgreSQL as the database with connection configured via DATABASE_URL environment variable.

**Error Handling & Responses:**

- **FR-049**: System MUST return all errors in JSON format with structure `{"error": "Human-readable message"}`.
- **FR-050**: System MUST use standard HTTP status codes: 200 (OK), 201 (Created), 204 (No Content), 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found), 409 (Conflict), 500 (Internal Server Error).
- **FR-051**: System MUST log all 5xx errors (server errors) with stack traces for debugging while returning generic error messages to clients.
- **FR-052**: System MUST NOT expose internal implementation details (e.g., database schema, file paths, stack traces) in error responses to clients.
- **FR-053**: System MUST handle Pydantic validation errors and convert them to 400 Bad Request responses with user-friendly error messages.

**API Design & Integration:**

- **FR-054**: System MUST use Pydantic v2 models for all request body validation and response serialization.
- **FR-055**: System MUST serialize datetime fields (created_at, updated_at) in ISO 8601 format with UTC timezone (e.g., "2026-01-09T10:30:00Z").
- **FR-056**: System MUST configure CORS to allow requests from the frontend origin (configurable via environment variable, e.g., FRONTEND_URL=http://localhost:3000).
- **FR-057**: System MUST allow CORS for methods: GET, POST, PUT, DELETE, OPTIONS.
- **FR-058**: System MUST allow CORS for headers: Authorization, Content-Type.
- **FR-059**: System MUST include appropriate CORS headers in all responses, including preflight OPTIONS requests.

**Configuration & Environment:**

- **FR-060**: System MUST load configuration from environment variables: DATABASE_URL, BETTER_AUTH_SECRET, FRONTEND_URL (for CORS), JWT_EXPIRATION_HOURS (default 24).
- **FR-061**: System MUST validate that required environment variables are present at startup and exit with clear error message if any are missing.
- **FR-062**: System MUST provide a health check endpoint GET /health that returns 200 OK with `{"status": "healthy"}` for deployment readiness checks.

### Key Entities

- **User**: Represents a registered user account. Managed by Better Auth on the frontend but stored in the backend database with fields: id (UUID), email (unique string), password_hash (bcrypt hash), created_at (timestamp). Used for authentication and task ownership.

- **Task**: Represents a todo item belonging to a user. Fields: id (UUID), title (string, required, max 255 chars), description (text, optional, max 1000 chars), completed (boolean, default false), user_id (UUID foreign key to User), created_at (timestamp, auto-set), updated_at (timestamp, auto-updated). Enforces user isolation via user_id filtering.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Backend responds to authenticated requests with valid JWT tokens within 200ms (p95 latency) under normal load.

- **SC-002**: Backend correctly validates JWT signatures and rejects 100% of requests with invalid or expired tokens with 401 Unauthorized.

- **SC-003**: Backend enforces strict data isolation such that 0% of requests return tasks belonging to a different user than the authenticated user.

- **SC-004**: Backend handles at least 100 concurrent authenticated task list requests without errors or timeout.

- **SC-005**: Backend successfully creates and persists new tasks to Neon PostgreSQL with 99.9% reliability under normal network conditions.

- **SC-006**: Backend returns clear, actionable error messages (no stack traces or internal details exposed) for 100% of client errors (4xx status codes).

- **SC-007**: Backend startup process completes within 10 seconds and fails fast with clear error messages if required environment variables are missing.

- **SC-008**: Backend maintains database connection pool efficiently, supporting at least 50 concurrent database connections to Neon.

- **SC-009**: Backend API contracts (request/response formats, status codes) are 100% compatible with the frontend specification in specs/001-frontend-ui/contracts/api-endpoints.md.

- **SC-010**: Backend handles malicious inputs (SQL injection attempts, XSS payloads, oversized requests) safely without crashing or exposing vulnerabilities.

## Assumptions *(document reasonable defaults)*

### Authentication Assumptions

- **A-001**: Better Auth is NOT directly integrated into the backend; the backend only validates JWT tokens signed by Better Auth using a shared secret (BETTER_AUTH_SECRET).

- **A-002**: JWT tokens use HS256 (HMAC with SHA-256) signing algorithm with the shared secret.

- **A-003**: JWT tokens contain standard claims: user_id (subject), email, exp (expiration), iat (issued at). The backend does not implement token refresh logic in Phase II.

- **A-004**: Token expiration is set to 24 hours by default. Expired tokens are rejected and users must re-authenticate via the frontend.

### Database Assumptions

- **A-005**: Neon Serverless PostgreSQL is pre-configured and accessible via DATABASE_URL connection string. The backend does not handle database provisioning.

- **A-006**: Database schema is created via SQLModel's `create_all()` method or a lightweight migration tool (e.g., Alembic). No complex migration rollback strategy is required for hackathon Phase II.

- **A-007**: Database connection pooling is handled by SQLModel/SQLAlchemy with reasonable defaults (e.g., pool size 5-10 connections). No custom connection pool tuning in Phase II.

- **A-008**: The users table exists and is managed by Better Auth or a separate user management system. The backend only references users via user_id foreign key and does not manage user CRUD operations beyond signup/login.

### API Assumptions

- **A-009**: All API endpoints are prefixed with /api (e.g., /api/tasks, /api/auth/login) to differentiate backend routes from frontend routes.

- **A-010**: The backend runs on a separate port from the frontend (e.g., backend on :8000, frontend on :3000) during development. CORS is configured to allow cross-origin requests from the frontend.

- **A-011**: No pagination is required for task lists in Phase II. The backend returns all tasks for a user (reasonable assumption: <100 tasks per user).

- **A-012**: No advanced filtering, sorting (beyond default created_at descending), or search functionality is required in Phase II.

### Security Assumptions

- **A-013**: HTTPS/TLS termination is handled by a reverse proxy (e.g., Nginx, AWS ALB) in production. The backend application itself listens on HTTP.

- **A-014**: Rate limiting and DDoS protection are handled at the infrastructure level (e.g., API gateway, load balancer). No application-level rate limiting in Phase II.

- **A-015**: Input sanitization for XSS prevention is primarily a frontend concern since the backend returns JSON (not HTML). The backend validates and truncates input lengths via Pydantic.

### Operational Assumptions

- **A-016**: The backend is deployed as a single containerized application (e.g., Docker) with environment variables injected at runtime.

- **A-017**: Application logs are written to stdout/stderr and collected by a log aggregation system (e.g., CloudWatch, Datadog). No custom logging infrastructure in Phase II.

- **A-018**: Health check endpoint (/health) is used by orchestration platforms (e.g., Kubernetes, ECS) for readiness and liveness probes.

## Dependencies

### External Dependencies

- **Python 3.11+**: Runtime environment for FastAPI application.
- **FastAPI**: Modern web framework for building REST APIs with automatic OpenAPI documentation.
- **SQLModel**: ORM library combining SQLAlchemy and Pydantic for type-safe database models.
- **Pydantic v2**: Data validation and serialization library.
- **PyJWT**: Library for encoding and decoding JWT tokens.
- **Passlib (with bcrypt)**: Password hashing library for secure credential storage.
- **Uvicorn**: ASGI server for running FastAPI applications.
- **Python-dotenv**: Library for loading environment variables from .env files (development only).

### Database Dependencies

- **Neon Serverless PostgreSQL**: Cloud-native Postgres database accessible via standard PostgreSQL connection string.
- **Psycopg2 or Asyncpg**: PostgreSQL database adapter for Python (SQLModel/SQLAlchemy dependency).

### Frontend Dependencies

- Frontend application at FRONTEND_URL origin must send JWT tokens via Authorization header.
- Frontend must handle token storage, attachment to requests, and logout/token clearing.

### Environment Configuration

- **DATABASE_URL**: PostgreSQL connection string in format `postgresql://user:password@host:port/database` (provided by Neon).
- **BETTER_AUTH_SECRET**: Shared secret for JWT signature verification (same secret used by Better Auth on frontend).
- **FRONTEND_URL**: Frontend origin for CORS configuration (e.g., `http://localhost:3000` in development, `https://app.example.com` in production).
- **JWT_EXPIRATION_HOURS**: Token expiration time in hours (default: 24).

## Out of Scope (Phase II)

**Explicitly excluded from this specification:**

- Frontend implementation (already specified in specs/001-frontend-ui)
- Better Auth library integration or user management UI
- Token refresh or refresh token logic
- Password reset or forgot password flows
- Email verification or account activation
- Multi-factor authentication (MFA)
- OAuth2 or social login providers
- User profile management (update email, change password)
- User account deletion
- Task sharing or collaboration features
- Real-time updates (WebSockets, Server-Sent Events)
- Task categories, tags, or labels
- Task priorities or due dates
- Task comments or attachments
- Task history or audit logs
- Soft deletes or trash/archive functionality
- Database migrations with rollback strategy (use simple create_all() approach)
- Advanced query optimization or database indexing beyond basic user_id index
- Caching layer (Redis, Memcached)
- Full-text search
- GraphQL API (REST only)
- API versioning (single version /api)
- API documentation generation beyond FastAPI's automatic OpenAPI docs
- Monitoring, alerting, or observability tooling
- Distributed tracing (OpenTelemetry, Jaeger)
- Automated testing infrastructure (unit/integration tests are recommended but not specified here)
- CI/CD pipeline configuration
- Container orchestration (Kubernetes manifests, Docker Compose)
- Infrastructure as Code (Terraform, CloudFormation)
- Performance benchmarking or load testing
- Security scanning or penetration testing
- GDPR compliance or data export features
- Internationalization (i18n) or localization

## Additional Specifications Referenced

This specification should be implemented alongside the following detailed technical plans (to be created during the planning phase):

- **specs/002-backend-api/plan.md**: Detailed architecture plan including module structure, dependency injection, middleware stack, and error handling strategy.
- **specs/002-backend-api/tasks.md**: Implementation task breakdown with acceptance criteria for each module.
- **specs/002-backend-api/api-reference.md**: Complete OpenAPI/Swagger documentation for all endpoints (can be auto-generated by FastAPI).
- **specs/002-backend-api/database-schema.sql**: Database schema DDL for manual review and migration tracking.
- **specs/002-backend-api/deployment.md**: Deployment guide for local development and production environments.
