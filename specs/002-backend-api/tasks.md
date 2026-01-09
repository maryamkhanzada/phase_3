# Implementation Tasks: Backend REST API for Todo Application

**Feature Branch**: `002-backend-api`
**Date**: 2026-01-09
**Spec**: [spec.md](./spec.md)
**Plan**: [plan.md](./plan.md)

## Overview

This document breaks down the backend implementation into atomic, executable tasks organized by user story priority. Each user story can be implemented and tested independently, enabling incremental delivery and parallel development.

**Total Tasks**: 52
**User Stories**: 6 (P1-P6)
**Parallelizable Tasks**: 28

---

## Implementation Strategy

### MVP Scope (Recommended First Iteration)

**User Story 1 (P1)**: JWT Authentication & Validation
- **Value**: Security foundation - blocks all other work until complete
- **Test**: Send requests with valid/invalid/expired/missing tokens
- **Deliverable**: Authentication middleware functional

### Incremental Delivery Order

1. **US1 (P1)**: Authentication infrastructure → Enables all protected endpoints
2. **US2 (P2)**: Signup/Login endpoints → Users can obtain tokens
3. **US3 (P3)**: Fetch tasks → Users can view their data
4. **US4 (P4)**: Create tasks → Users can add data
5. **US5 (P5)**: Update tasks → Users can modify data
6. **US6 (P6)**: Delete tasks → Users can remove data

Each story is independently testable and deliverable.

---

## Phase 1: Setup & Project Initialization

**Objective**: Create backend project structure, install dependencies, configure environment.

**Dependencies**: None (first phase)

**Completion Criteria**: Python venv active, all dependencies installed, .env configured

### Tasks

- [x] T001 Create backend/ directory structure (backend/src/, backend/tests/)
- [x] T002 Create Python virtual environment (python -m venv venv)
- [x] T003 [P] Create requirements.txt with dependencies (FastAPI, SQLModel, PyJWT, Passlib, asyncpg, pydantic-settings, python-dotenv, uvicorn)
- [x] T004 [P] Create .gitignore for Python (venv/, __pycache__/, .env, *.pyc)
- [x] T005 Install dependencies (pip install -r requirements.txt)
- [x] T006 Create .env template with required variables (DATABASE_URL, BETTER_AUTH_SECRET, FRONTEND_URL, JWT_EXPIRATION_HOURS)
- [x] T007 [P] Create backend/README.md with setup instructions

---

## Phase 2: Foundational Infrastructure

**Objective**: Implement core infrastructure needed by ALL user stories (configuration, database, base models).

**Dependencies**: Phase 1 (Setup complete)

**Completion Criteria**: Configuration loads, database connects, models defined

### Tasks

- [x] T008 [P] Implement configuration module in backend/src/config.py using Pydantic Settings
- [x] T009 [P] Implement database connection module in backend/src/db.py (async SQLAlchemy engine, session dependency)
- [x] T010 [P] Implement User model in backend/src/models.py (SQLModel with id, email, password_hash, created_at)
- [x] T011 [P] Implement Task model in backend/src/models.py (SQLModel with id, title, description, completed, user_id, created_at, updated_at)
- [x] T012 [P] Implement custom exceptions in backend/src/exceptions.py (UnauthorizedException, ForbiddenException, NotFoundException)
- [x] T013 Implement database initialization function in backend/src/db.py (init_db using create_all)
- [x] T014 [P] Create backend/src/auth/__init__.py
- [x] T015 [P] Create backend/src/routes/__init__.py
- [x] T016 [P] Create backend/src/schemas/__init__.py

---

## Phase 3: User Story 1 - JWT Authentication & Validation (P1)

**Story Goal**: Authenticate every incoming request using JWT tokens, extract user identity, enforce data isolation.

**Why Independent**: Foundation for all protected endpoints. Can be tested with mock endpoints.

**Independent Test**:
1. Create test endpoint requiring authentication
2. Send request with valid token → 200 OK, user_id extracted
3. Send request with invalid signature → 401 Unauthorized
4. Send request with expired token → 401 Unauthorized
5. Send request without token → 401 Unauthorized
6. Send request with malformed header → 401 Unauthorized

**Deliverable**: JWT validation dependency functional, returns user_id or raises 401.

### Tasks

- [x] T017 [US1] Implement password hashing utilities in backend/src/auth/password.py (hash_password using bcrypt, verify_password)
- [x] T018 [US1] Implement JWT verification function in backend/src/auth/jwt.py (verify_jwt_token validates signature, expiration, extracts user_id)
- [x] T019 [US1] Implement get_current_user FastAPI dependency in backend/src/auth/jwt.py (extracts Authorization header, calls verify_jwt_token, returns user_id)
- [x] T020 [US1] Test JWT verification with valid token (decode token, verify user_id extracted correctly)
- [x] T021 [US1] Test JWT verification with invalid signature (verify 401 Unauthorized returned)
- [x] T022 [US1] Test JWT verification with expired token (verify 401 Unauthorized returned)
- [x] T023 [US1] Test JWT verification with missing Authorization header (verify 401 Unauthorized returned)

---

## Phase 4: User Story 2 - User Registration & Login (P2)

**Story Goal**: Provide signup and login endpoints that create accounts and issue JWT tokens.

**Why Independent**: Enables token acquisition. Can be tested by creating users and logging in.

**Independent Test**:
1. POST /api/auth/signup with valid credentials → 201 Created with token
2. POST /api/auth/signup with duplicate email → 409 Conflict
3. POST /api/auth/signup with invalid email → 400 Bad Request
4. POST /api/auth/signup with short password → 400 Bad Request
5. POST /api/auth/login with valid credentials → 200 OK with token
6. POST /api/auth/login with wrong password → 401 Unauthorized

**Deliverable**: Users can signup and login via /docs interface.

### Tasks

- [x] T024 [P] [US2] Implement auth request schemas in backend/src/schemas/auth.py (SignupRequest, LoginRequest with email validation)
- [x] T025 [P] [US2] Implement auth response schemas in backend/src/schemas/auth.py (AuthResponse, UserResponse excluding password_hash)
- [x] T026 [US2] Implement POST /api/auth/signup endpoint in backend/src/routes/auth.py (validate input, hash password, create User, generate JWT, return 201)
- [x] T027 [US2] Implement POST /api/auth/login endpoint in backend/src/routes/auth.py (validate credentials, verify password, generate JWT, return 200)
- [x] T028 [US2] Test signup with valid credentials (verify 201, token returned, user created in DB)
- [x] T029 [US2] Test signup with duplicate email (verify 409 Conflict)
- [x] T030 [US2] Test signup with invalid email format (verify 400 Bad Request)
- [x] T031 [US2] Test login with valid credentials (verify 200, token returned)
- [x] T032 [US2] Test login with incorrect password (verify 401 Unauthorized)

---

## Phase 5: User Story 3 - Fetch User's Task List (P3)

**Story Goal**: Retrieve all tasks belonging to authenticated user with strict user isolation.

**Why Independent**: First read operation. Can be tested by creating tasks for multiple users and verifying isolation.

**Independent Test**:
1. Create User A with 5 tasks, User B with 3 tasks
2. Authenticate as User A, GET /api/tasks → 200 OK with 5 tasks (only User A's)
3. Authenticate as User B, GET /api/tasks → 200 OK with 3 tasks (only User B's)
4. Verify User A cannot see User B's tasks
5. Send GET /api/tasks without token → 401 Unauthorized
6. User with no tasks → 200 OK with empty array

**Deliverable**: Task list endpoint with verified user isolation.

### Tasks

- [x] T033 [P] [US3] Implement task response schemas in backend/src/schemas/task.py (TaskResponse, TaskListResponse)
- [x] T034 [US3] Implement GET /api/tasks endpoint in backend/src/routes/tasks.py (filter by user_id from JWT, order by created_at DESC, return tasks array)
- [x] T035 [US3] Test GET /api/tasks with authenticated user (verify tasks filtered by user_id)
- [x] T036 [US3] Test GET /api/tasks with no tasks (verify empty array returned)
- [x] T037 [US3] Test user isolation (create tasks for 2 users, verify each sees only their own)
- [x] T038 [US3] Test GET /api/tasks without authentication (verify 401 Unauthorized)

---

## Phase 6: User Story 4 - Create New Task (P4)

**Story Goal**: Create new tasks automatically assigned to authenticated user (never trust client user_id).

**Why Independent**: First write operation. Can be tested by creating tasks and verifying user_id assignment.

**Independent Test**:
1. Authenticate as User A, POST /api/tasks with title/description → 201 Created, task.user_id = User A's ID
2. Verify User B cannot see task created by User A
3. POST /api/tasks without title → 400 Bad Request
4. POST /api/tasks with empty title → 400 Bad Request
5. POST /api/tasks without token → 401 Unauthorized

**Deliverable**: Task creation endpoint with automatic user assignment.

### Tasks

- [x] T039 [P] [US4] Implement task creation request schema in backend/src/schemas/task.py (TaskCreateRequest with title validation)
- [x] T040 [US4] Implement POST /api/tasks endpoint in backend/src/routes/tasks.py (validate title, set user_id from JWT, set defaults, create Task, return 201)
- [x] T041 [US4] Test POST /api/tasks with valid data (verify 201, task created with correct user_id)
- [x] T042 [US4] Test POST /api/tasks without title (verify 400 Bad Request)
- [x] T043 [US4] Test POST /api/tasks with empty title (verify 400 Bad Request)
- [x] T044 [US4] Test POST /api/tasks without authentication (verify 401 Unauthorized)
- [x] T045 [US4] Test user_id assignment (verify task.user_id matches JWT user_id, not from request body)

---

## Phase 7: User Story 5 - Update Task (P5)

**Story Goal**: Allow users to update their own tasks while preventing unauthorized access.

**Why Independent**: Enhancement operation. Can be tested by creating and updating tasks with ownership verification.

**Independent Test**:
1. User A creates task, updates it → 200 OK with updated task
2. User A attempts to update User B's task → 404 Not Found
3. PUT /api/tasks/:id with empty title → 400 Bad Request
4. PUT /api/tasks/:nonexistent-id → 404 Not Found
5. PUT /api/tasks/:id with partial update (only completed) → 200 OK, only completed changed

**Deliverable**: Task update endpoint with ownership verification.

### Tasks

- [x] T046 [P] [US5] Implement task update request schema in backend/src/schemas/task.py (TaskUpdateRequest with optional fields)
- [x] T047 [US5] Implement PUT /api/tasks/:id endpoint in backend/src/routes/tasks.py (verify ownership, validate input, partial update, update updated_at, return 200)
- [x] T048 [US5] Test PUT /api/tasks/:id with valid update (verify 200, task updated, updated_at changed)
- [x] T049 [US5] Test PUT /api/tasks/:id with wrong owner (verify 404 Not Found for security)
- [x] T050 [US5] Test PUT /api/tasks/:id with empty title (verify 400 Bad Request)
- [x] T051 [US5] Test PUT /api/tasks/:id with partial update (verify only provided fields updated)

---

## Phase 8: User Story 6 - Delete Task (P6)

**Story Goal**: Allow users to permanently delete their own tasks with authorization checks.

**Why Independent**: Maintenance operation. Can be tested by creating and deleting tasks with ownership verification.

**Independent Test**:
1. User A creates task, deletes it → 204 No Content, task removed from DB
2. User A attempts to delete User B's task → 404 Not Found
3. DELETE /api/tasks/:nonexistent-id → 404 Not Found
4. Verify deleted task cannot be fetched (404 on GET)

**Deliverable**: Task deletion endpoint with ownership verification.

### Tasks

- [x] T052 [US6] Implement DELETE /api/tasks/:id endpoint in backend/src/routes/tasks.py (verify ownership, delete task, return 204)
- [x] T053 [US6] Test DELETE /api/tasks/:id with valid deletion (verify 204, task removed from database)
- [x] T054 [US6] Test DELETE /api/tasks/:id with wrong owner (verify 404 Not Found for security)
- [x] T055 [US6] Test DELETE /api/tasks/:id for nonexistent task (verify 404 Not Found)

---

## Phase 9: Application Setup & Integration

**Objective**: Wire up FastAPI app with routers, middleware, exception handlers.

**Dependencies**: All user story phases (US1-US6) complete

**Completion Criteria**: uvicorn runs, /docs accessible, CORS works, all endpoints registered

### Tasks

- [x] T056 Create FastAPI app instance in backend/src/main.py
- [x] T057 Configure CORS middleware in backend/src/main.py (allow FRONTEND_URL, credentials, methods, headers)
- [x] T058 Register auth router in backend/src/main.py (app.include_router with /api/auth prefix)
- [x] T059 Register tasks router in backend/src/main.py (app.include_router with /api prefix)
- [x] T060 Add startup event to initialize database in backend/src/main.py (call init_db)
- [x] T061 [P] Implement global exception handler for Pydantic ValidationError (convert 422 → 400)
- [x] T062 [P] Implement GET /health endpoint (return {"status": "healthy"})
- [x] T063 Test FastAPI app starts successfully (uvicorn src.main:app --reload)
- [x] T064 Test /docs accessible and shows all endpoints
- [x] T065 Test CORS headers present in OPTIONS preflight requests

---

## Phase 10: Polish & Final Validation

**Objective**: Final testing, documentation, deployment readiness.

**Dependencies**: Phase 9 (Application setup) complete

**Completion Criteria**: All acceptance tests pass, multi-user isolation verified, frontend integration ready

### Tasks

- [x] T066 Run full signup flow via /docs (create account, verify token returned)
- [x] T067 Run full login flow via /docs (login, verify token returned)
- [x] T068 Run full task CRUD flow via /docs (create, read, update, delete tasks)
- [x] T069 Verify user isolation with 2 test users (User A cannot see/modify User B's tasks)
- [x] T070 Test all error cases (401, 400, 404, 409 responses)
- [x] T071 Verify datetime serialization (ISO 8601 UTC format in responses)
- [x] T072 Verify API responses match frontend contracts exactly
- [x] T073 Update backend/README.md with run instructions and API documentation link
- [x] T074 Create backend deployment checklist (environment variables, database migration, health check)

---

## Dependency Graph

### User Story Completion Order

```
Setup (Phase 1)
    ↓
Foundational (Phase 2)
    ↓
US1: Authentication (P1) ← MUST complete first (blocks all protected endpoints)
    ↓
US2: Signup/Login (P2) ← MUST complete second (enables token acquisition)
    ↓
┌───────────────────────────────────────┐
│ US3: Fetch Tasks (P3)                 │← Can run in parallel
│ US4: Create Task (P4)                 │← Can run in parallel
│ US5: Update Task (P5)                 │← Can run in parallel
│ US6: Delete Task (P6)                 │← Can run in parallel
└───────────────────────────────────────┘
    ↓
Application Setup (Phase 9)
    ↓
Polish & Validation (Phase 10)
```

**Critical Path**: Setup → Foundational → US1 → US2 → US3-6 (parallel) → App Setup → Polish

**Parallelization Opportunities**:
- After US2 complete: US3, US4, US5, US6 can all be implemented in parallel by different developers
- Setup tasks (T003, T004, T007) can run in parallel
- Foundational tasks (T008-T016) can run in parallel
- Schema tasks within each user story (T024-T025, T033, T039, T046) can run in parallel

---

## Parallel Execution Examples

### Example 1: Four Developers After US2 Complete

**Developer 1**: US3 (Fetch Tasks)
- T033-T038

**Developer 2**: US4 (Create Task)
- T039-T045

**Developer 3**: US5 (Update Task)
- T046-T051

**Developer 4**: US6 (Delete Task)
- T052-T055

All four user stories are independent and can be developed simultaneously.

### Example 2: Parallelizing Foundational Phase

**Developer 1**: Configuration & Database
- T008, T009, T013

**Developer 2**: Models
- T010, T011

**Developer 3**: Exceptions & Structure
- T012, T014, T015, T016

---

## Testing Strategy

### User Story Independent Tests

Each user story has clear independent test criteria that can be executed without other stories:

**US1 (Authentication)**:
- Mock protected endpoint, test JWT validation with various token states

**US2 (Signup/Login)**:
- Test auth endpoints via /docs, verify token generation and user creation

**US3 (Fetch Tasks)**:
- Create tasks directly in DB for test users, verify GET /api/tasks isolation

**US4 (Create Task)**:
- Test POST /api/tasks, verify automatic user_id assignment

**US5 (Update Task)**:
- Create task, test PUT /api/tasks/:id with ownership scenarios

**US6 (Delete Task)**:
- Create task, test DELETE /api/tasks/:id with ownership scenarios

### Integration Tests

After Phase 10, run full end-to-end tests:
1. Signup user → login → create task → fetch tasks → update task → delete task
2. Multi-user isolation: 2 users each with separate tasks

---

## Task Summary

| Phase | User Story | Task Count | Parallelizable | Independent Test Defined |
|-------|------------|------------|----------------|-------------------------|
| **1** | Setup | 7 | 3 | ✅ Dependencies installed |
| **2** | Foundational | 9 | 8 | ✅ Config loads, DB connects |
| **3** | US1 (P1) | 7 | 0 | ✅ JWT validation works |
| **4** | US2 (P2) | 9 | 2 | ✅ Signup/login functional |
| **5** | US3 (P3) | 6 | 1 | ✅ Task fetch with isolation |
| **6** | US4 (P4) | 7 | 1 | ✅ Task creation secure |
| **7** | US5 (P5) | 6 | 1 | ✅ Task update authorized |
| **8** | US6 (P6) | 4 | 0 | ✅ Task deletion authorized |
| **9** | App Setup | 10 | 2 | ✅ App runs, CORS works |
| **10** | Polish | 9 | 0 | ✅ All tests pass |
| **Total** | - | **74** | **18** | ✅ All stories testable |

---

## MVP Recommendation

**Minimum Viable Product**: Complete through US2 (Signup/Login)

**Scope**:
- Setup + Foundational (T001-T016)
- US1: Authentication (T017-T023)
- US2: Signup/Login (T024-T032)
- App Setup (T056-T065)
- Basic validation (T066-T067)

**Total MVP Tasks**: ~35 tasks
**Deliverable**: Backend with working authentication, users can signup/login and receive JWT tokens

**Next Increment**: Add US3 (Fetch Tasks) to enable read operations
**Full Feature**: Complete all US1-US6 for complete CRUD functionality

---

## Implementation Notes

### Critical Security Checkpoints

**After T019 (get_current_user dependency)**:
- Verify dependency correctly extracts user_id from JWT
- Verify 401 returned for invalid/missing/expired tokens

**After T034 (GET /api/tasks endpoint)**:
- Verify tasks filtered by user_id (run T037 isolation test)

**After T040 (POST /api/tasks endpoint)**:
- Verify user_id set from JWT, not from request body (run T045 test)

**After T047 (PUT /api/tasks/:id endpoint)**:
- Verify ownership check prevents cross-user updates (run T049 test)

**After T052 (DELETE /api/tasks/:id endpoint)**:
- Verify ownership check prevents cross-user deletions (run T054 test)

### Common Patterns

**JWT Verification**:
```python
from fastapi import Depends
from src.auth.jwt import get_current_user

@router.get("/api/tasks")
async def get_tasks(current_user_id: str = Depends(get_current_user)):
    # current_user_id is guaranteed to be from validated JWT
```

**User Isolation Query**:
```python
# CORRECT - filters by user_id
tasks = await session.execute(
    select(Task).where(Task.user_id == current_user_id)
)

# WRONG - missing user_id filter (security vulnerability)
tasks = await session.execute(select(Task))  # Returns ALL users' tasks!
```

**Ownership Verification**:
```python
# CORRECT - combined existence + ownership check
task = await session.execute(
    select(Task).where(Task.id == task_id).where(Task.user_id == current_user_id)
).scalar_one_or_none()

if not task:
    raise NotFoundException()  # 404 (doesn't exist OR not owned)
```

---

## References

- [Specification](./spec.md) - User stories and acceptance criteria
- [Implementation Plan](./plan.md) - Architecture and tech stack decisions
- [API Contracts](./contracts/api-endpoints.md) - Endpoint specifications
- [Data Model](./data-model.md) - Database schema
- [Quick Start Guide](./quickstart.md) - Development setup

---

**Next Steps**:
1. Review tasks with team
2. Assign user stories to developers
3. Implement US1-US2 for MVP
4. Test independently per story
5. Integrate and deploy incrementally
