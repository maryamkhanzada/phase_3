# Implementation Plan: Backend REST API for Todo Application

**Branch**: `002-backend-api` | **Date**: 2026-01-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-backend-api/spec.md`

## Summary

Build a secure, production-ready FastAPI backend that provides REST API endpoints for user authentication and task management. The backend enforces JWT-based authentication, strict user data isolation, and integrates seamlessly with the Next.js frontend. All API contracts are finalized in `contracts/api-endpoints.md` and must be implemented exactly as specified to ensure frontend compatibility.

**Technical Approach**: Use FastAPI with async SQLModel ORM for Neon PostgreSQL, PyJWT for token validation, Passlib for password hashing, and Pydantic for request/response validation. Implement FastAPI dependency injection for authentication middleware and structured exception handling for consistent error responses.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.109+, SQLModel 0.0.14, PyJWT 2.8, Passlib 1.7, Pydantic 2.x
**Storage**: Neon Serverless PostgreSQL (asyncpg driver)
**Testing**: pytest + pytest-asyncio (post-Phase II)
**Target Platform**: Linux/Docker container (ASGI server via Uvicorn)
**Project Type**: Web backend (API server)
**Performance Goals**: <200ms p95 latency for authenticated requests, 100+ concurrent connections
**Constraints**: 100% frontend API contract compatibility, zero cross-user data leakage
**Scale/Scope**: <100 tasks per user (no pagination in Phase II), 6 API endpoints, 2 database tables

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Spec-First Development**: Backend spec fully defined in `specs/002-backend-api/spec.md` with 62 functional requirements

✅ **Authentication & Security**: JWT validation enforced via FastAPI dependency, user isolation via database query filtering

✅ **API Design & RESTful Standards**: All endpoints follow REST conventions under `/api/` prefix with correct HTTP verbs/status codes

✅ **Data Ownership & User Isolation**: Every task query filters by `user_id` from JWT token (never from client request)

✅ **Tech Stack Enforcement**: Backend uses mandated stack (FastAPI, SQLModel, PostgreSQL, JWT)

✅ **Instruction Hierarchy**: Implementation follows spec → CLAUDE.md → Constitution priority order

✅ **Phase-Aware Implementation**: Backend implements ONLY Phase II features (no chatbot, no mobile apps)

## Project Structure

### Documentation (this feature)

```text
specs/002-backend-api/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0: Technical decisions & research
├── data-model.md        # Phase 1: Database schema & entities
├── quickstart.md        # Phase 1: Developer setup guide
├── contracts/           # Phase 1: API endpoint contracts
│   └── api-endpoints.md # REST API specification
├── checklists/
│   └── requirements.md  # Spec quality validation
└── tasks.md             # Phase 2: NOT created yet (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py             # FastAPI app entry point + middleware setup
│   ├── config.py           # Pydantic Settings for env vars
│   ├── db.py               # SQLModel async engine + session dependency
│   ├── models.py           # User & Task SQLModel classes
│   ├── exceptions.py       # Custom HTTPException subclasses
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt.py          # JWT verification dependency
│   │   └── password.py     # Bcrypt password hashing
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py         # POST /api/auth/signup, /login
│   │   └── tasks.py        # Task CRUD endpoints
│   └── schemas/
│       ├── __init__.py
│       ├── auth.py         # AuthRequest, AuthResponse, UserResponse
│       └── task.py         # TaskCreateRequest, TaskUpdateRequest, TaskResponse
├── tests/                  # Future: pytest test suite
│   ├── conftest.py         # Shared fixtures (test client, auth)
│   ├── unit/               # Unit tests (auth, password, utils)
│   └── integration/        # API endpoint tests
├── .env                    # Environment variables (NOT committed to git)
├── .gitignore              # Git ignore (.env, venv/, __pycache__, etc.)
├── requirements.txt        # Python dependencies
└── README.md               # Backend setup and run instructions
```

**Structure Decision**: Web application backend using Option 2 pattern. Backend runs as standalone ASGI application on port 8000, frontend (already implemented in `frontend/`) runs on port 3000. Backend serves ONLY API endpoints under `/api/*` prefix. No static file serving or HTML templates.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations** - All constitution gates passed. Implementation uses standard FastAPI patterns with minimal abstraction layers.

---

## Implementation Sequence

Implementation follows strict dependency order to ensure each module builds on completed work.

| Phase | Module | Files | Dependencies | Validation |
|-------|--------|-------|--------------|------------|
| **1** | Project Init | backend/, requirements.txt, .env | None | pip install succeeds |
| **2** | Configuration | src/config.py | Phase 1 | Import settings without ValidationError |
| **3** | Database | src/db.py, src/models.py | Phase 2 | init_db() creates tables in Neon |
| **4** | Auth Layer | src/auth/jwt.py, src/auth/password.py | Phase 2-3 | Verify JWT, hash/check password |
| **5** | Schemas | src/schemas/auth.py, src/schemas/task.py | Phase 3 | FastAPI generates OpenAPI schema |
| **6** | Exceptions | src/exceptions.py | None | Raise exception → JSON response |
| **7** | Auth Routes | src/routes/auth.py | Phase 2-6 | Signup/login via /docs |
| **8** | Task Routes | src/routes/tasks.py | Phase 3-6 | CRUD operations via /docs |
| **9** | App Setup | src/main.py | Phase 3,7,8 | uvicorn runs, /docs accessible, CORS works |
| **10** | Error Handling | src/main.py (handlers) | Phase 9 | Invalid request → 400, not 422 |
| **11** | Integration Check | N/A (validation) | All phases | API responses match contracts |
| **12** | Final Testing | N/A (testing) | All phases | Multi-user isolation verified |

### Critical Security Checkpoints

After Phase 8 (Task Routes), verify:
- [ ] User A cannot see User B's tasks (GET /api/tasks filtered by user_id)
- [ ] User A cannot update User B's task (PUT returns 404)
- [ ] User A cannot delete User B's task (DELETE returns 404)
- [ ] user_id always comes from JWT, never from request body/URL

---

## Key Implementation Details

### JWT Verification (Phase 4)

FastAPI dependency that:
1. Extracts token from Authorization header (format: "Bearer <token>")
2. Decodes JWT using PyJWT with BETTER_AUTH_SECRET
3. Validates signature (HS256 algorithm)
4. Checks expiration (exp claim)
5. Extracts user_id from payload
6. Raises 401 if any step fails

### User Isolation (Phase 8)

ALL task queries use this pattern:
```python
# CORRECT (enforces isolation)
task = session.execute(
    select(Task).where(Task.id == task_id).where(Task.user_id == current_user_id)
).scalar_one_or_none()

# WRONG (security vulnerability)
task = session.get(Task, task_id)  # Missing user_id check!
```

### Password Security (Phase 4, 7)

- Signup: hash_password(plaintext) → store in password_hash field
- Login: verify_password(plaintext, stored_hash) → boolean
- NEVER store plaintext passwords
- NEVER return password_hash in API responses

---

## Integration with Frontend

**Backend Readiness Checklist**:
- [ ] All endpoints return exact field names expected by frontend
- [ ] Datetimes serialized as ISO 8601 UTC (Pydantic handles automatically)
- [ ] Error responses use {"error": "message"} format
- [ ] CORS allows http://localhost:3000 (development) or FRONTEND_URL (production)
- [ ] JWT tokens contain user_id and email claims

**Frontend Compatibility**: 100% - All contracts in `contracts/api-endpoints.md` match frontend expectations in `specs/001-frontend-ui/contracts/api-endpoints.md`.

---

## Next Steps

1. **Generate Tasks**: Run `/sp.tasks` to break down implementation into atomic tasks
2. **Implement**: Execute tasks in dependency order (Phase 1 → 12)
3. **Test**: Verify each phase's validation criteria before proceeding
4. **Integrate**: Connect with frontend and perform end-to-end testing
5. **Deploy**: (Future) Containerize backend, deploy to cloud platform

---

## References

- [Specification](./spec.md) - 62 functional requirements
- [Research](./research.md) - Technology decisions and rationale
- [Data Model](./data-model.md) - Database schema (User, Task)
- [API Contracts](./contracts/api-endpoints.md) - Endpoint specifications
- [Quick Start](./quickstart.md) - Developer setup guide
- [Frontend Contracts](../001-frontend-ui/contracts/api-endpoints.md) - Frontend expectations
