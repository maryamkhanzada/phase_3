# Research & Technical Decisions: Backend REST API

**Feature**: Backend REST API for Todo Application
**Branch**: `002-backend-api`
**Date**: 2026-01-09
**Phase**: 0 - Research

## Overview

This document consolidates all technical research and decisions for the backend implementation. All unknowns from the specification have been resolved through research, and concrete implementation approaches have been selected.

---

## 1. JWT Verification Strategy

### Decision

Use **PyJWT** library with FastAPI dependency injection for JWT validation.

### Rationale

- PyJWT is the standard JWT library for Python with 8.7k+ stars and wide adoption
- FastAPI's dependency injection system provides clean, reusable authentication logic
- Dependency functions can extract and validate JWT tokens before route handlers execute
- Enables easy testing by mocking the dependency
- Consistent with FastAPI best practices and ecosystem patterns

### Implementation Approach

1. Create `backend/src/auth/jwt.py` module with:
   - `verify_jwt_token(token: str) -> dict` function to validate signature and expiration
   - `get_current_user()` FastAPI dependency that extracts token from Authorization header, validates it, and returns user_id

2. Apply `get_current_user` dependency to all protected endpoints using `Depends()`

3. Configure JWT verification with:
   - Algorithm: HS256 (HMAC with SHA-256)
   - Secret: BETTER_AUTH_SECRET from environment
   - Claims validated: signature, exp (expiration), user_id/sub (subject)

### Alternatives Considered

- **python-jose**: More comprehensive but heavier dependency, includes unnecessary features for this use case
- **Manual JWT parsing**: Reinventing the wheel, error-prone, not worth the reduced dependency
- **Auth0 SDK**: Third-party service integration, unnecessary complexity for simple JWT validation

### References

- PyJWT documentation: https://pyjwt.readthedocs.io/
- FastAPI security documentation: https://fastapi.tiangolo.com/tutorial/security/

---

## 2. Password Hashing Strategy

### Decision

Use **Passlib** with **bcrypt** hashing algorithm.

### Rationale

- Bcrypt is cryptographically secure and designed for password hashing (not generic hashing)
- Passlib provides clean Python API for bcrypt and manages complexity (salting, cost factor)
- Bcrypt is deliberately slow (tunable cost factor) to resist brute-force attacks
- Industry-standard choice for password storage (OWASP recommended)
- FastAPI ecosystem commonly uses Passlib for password hashing

### Implementation Approach

1. Install `passlib[bcrypt]` dependency (includes bcrypt library)

2. Create `backend/src/auth/password.py` module with:
   - `hash_password(plain_password: str) -> str` - Hash password with bcrypt
   - `verify_password(plain_password: str, hashed_password: str) -> bool` - Verify password against hash

3. Configuration:
   - Default bcrypt cost factor: 12 (balance between security and performance)
   - Salt automatically handled by bcrypt

4. Usage:
   - Signup: `password_hash = hash_password(user_input_password)` → store in database
   - Login: `verify_password(user_input_password, stored_hash)` → returns True/False

### Alternatives Considered

- **Argon2**: Newer, theoretically stronger, but less ecosystem adoption in Python/FastAPI
- **scrypt**: Good alternative but bcrypt is more widely supported and tested
- **SHA-256 + manual salt**: NOT suitable for passwords (too fast, enables brute-force)

### References

- Passlib documentation: https://passlib.readthedocs.io/
- OWASP password storage: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

---

## 3. Database Connection Management

### Decision

Use **SQLModel** with **asyncpg** driver for async PostgreSQL connections.

### Rationale

- SQLModel combines SQLAlchemy ORM with Pydantic validation (perfect FastAPI integration)
- Async support enables non-blocking database operations (better concurrency under load)
- Neon Serverless PostgreSQL supports standard PostgreSQL protocol, compatible with asyncpg
- Connection pooling handled automatically by SQLAlchemy's async engine
- Type-safe models that double as Pydantic schemas for API responses

### Implementation Approach

1. Install dependencies: `sqlmodel`, `asyncpg`

2. Create `backend/src/db.py` module with:
   - `get_engine()` - Create async SQLAlchemy engine with DATABASE_URL
   - `init_db()` - Initialize database schema using `SQLModel.metadata.create_all()`
   - `get_session()` - FastAPI dependency for database sessions (async context manager)

3. Database connection pool configuration:
   - Pool size: 5 connections (reasonable default for Neon serverless)
   - Max overflow: 10 connections
   - Pool recycle: 3600 seconds (refresh connections hourly)

4. Usage pattern:
   ```python
   async def get_tasks(session: AsyncSession = Depends(get_session), user_id: str = Depends(get_current_user)):
       result = await session.execute(select(Task).where(Task.user_id == user_id))
       return result.scalars().all()
   ```

### Alternatives Considered

- **Synchronous SQLModel (psycopg2)**: Simpler but blocks event loop, reduces concurrency
- **Raw asyncpg**: Lower-level, more manual, loses ORM benefits
- **Tortoise ORM**: Async-first but smaller ecosystem than SQLAlchemy/SQLModel

### References

- SQLModel documentation: https://sqlmodel.tiangolo.com/
- FastAPI async SQL databases: https://fastapi.tiangolo.com/advanced/async-sql-databases/

---

## 4. Database Migration Strategy

### Decision

Use **SQLModel's `create_all()` method** for Phase II (hackathon simplicity); plan migration to **Alembic** for production.

### Rationale

- Phase II is a hackathon/prototype phase - simplicity trumps migration sophistication
- `create_all()` automatically creates tables based on SQLModel models
- No migration history needed for Phase II (fresh database setup)
- Alembic is the standard SQLAlchemy migration tool, available when needed later
- Avoids premature complexity for a feature set that's still evolving

### Implementation Approach

**Phase II (Current):**

1. On application startup, call `SQLModel.metadata.create_all(engine)`
2. This creates all tables if they don't exist (idempotent)
3. Schema changes require manual database reset (acceptable for development/hackathon)

**Future Migration Path (Production):**

1. Install `alembic` when ready for production
2. Generate initial migration from existing SQLModel models: `alembic revision --autogenerate`
3. Apply migrations: `alembic upgrade head`
4. Future schema changes: modify SQLModel → `alembic revision --autogenerate` → `alembic upgrade head`

### Alternatives Considered

- **Alembic from day 1**: Over-engineering for Phase II, adds complexity without current benefit
- **Manual SQL DDL scripts**: Error-prone, no type safety, harder to maintain
- **No migrations at all**: Acceptable for hackathon but not scalable

### References

- SQLModel metadata: https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/
- Alembic documentation: https://alembic.sqlalchemy.org/

---

## 5. CORS Configuration

### Decision

Use **FastAPI's built-in `CORSMiddleware`** with explicit origin whitelisting.

### Rationale

- CORSMiddleware is part of FastAPI's standard library (Starlette)
- Simple configuration via middleware registration
- Supports dynamic origin whitelisting via environment variable
- Handles preflight OPTIONS requests automatically
- No additional dependencies required

### Implementation Approach

1. Add CORSMiddleware to FastAPI app in `main.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
       allow_credentials=True,
       allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
       allow_headers=["Authorization", "Content-Type"],
   )
   ```

2. Configuration via environment variables:
   - Development: `FRONTEND_URL=http://localhost:3000`
   - Production: `FRONTEND_URL=https://app.yourdomain.com`

3. Security considerations:
   - Never use `allow_origins=["*"]` (wildcard) - explicit whitelisting only
   - `allow_credentials=True` enables cookies/auth headers if needed later

### Alternatives Considered

- **Manual CORS headers**: Reinventing the wheel, error-prone, misses preflight handling
- **Third-party CORS library**: Unnecessary dependency when FastAPI includes it

### References

- FastAPI CORS: https://fastapi.tiangolo.com/tutorial/cors/

---

## 6. Error Handling & Exception Strategy

### Decision

Use **FastAPI exception handlers** with custom `HTTPException` subclasses for domain-specific errors.

### Rationale

- FastAPI's exception handling integrates with Pydantic validation errors
- Custom exceptions provide type-safe, consistent error responses
- Centralized error handling reduces boilerplate in route handlers
- Automatic HTTP status code mapping via exception classes
- Easy to test and mock for different error scenarios

### Implementation Approach

1. Create `backend/src/exceptions.py` with custom exceptions:
   ```python
   class UnauthorizedException(HTTPException):
       def __init__(self, detail: str = "Unauthorized"):
           super().__init__(status_code=401, detail=detail)

   class ForbiddenException(HTTPException):
       def __init__(self, detail: str = "Access denied"):
           super().__init__(status_code=403, detail=detail)

   class NotFoundException(HTTPException):
       def __init__(self, detail: str = "Resource not found"):
           super().__init__(status_code=404, detail=detail)
   ```

2. Register global exception handlers in `main.py` to ensure consistent JSON error format

3. Usage in route handlers:
   ```python
   if not task:
       raise NotFoundException(detail="Task not found")
   if task.user_id != current_user_id:
       raise ForbiddenException(detail="Access denied")
   ```

4. Pydantic validation errors automatically return 422 Unprocessable Entity (convert to 400 via custom handler)

### Alternatives Considered

- **Manual `return JSONResponse(status_code=...)` everywhere**: Verbose, inconsistent, error-prone
- **Global try/except in middleware**: Works but less granular, harder to test specific errors

### References

- FastAPI exception handling: https://fastapi.tiangolo.com/tutorial/handling-errors/

---

## 7. Environment Variable Management

### Decision

Use **Pydantic `Settings`** class with **python-dotenv** for environment management.

### Rationale

- Pydantic Settings provides type validation for environment variables
- Automatic .env file loading in development (via python-dotenv)
- Type coercion (e.g., PORT="8000" → int(8000))
- Default values with validation
- Single source of truth for all configuration
- FastAPI integration best practice

### Implementation Approach

1. Create `backend/src/config.py`:
   ```python
   from pydantic_settings import BaseSettings

   class Settings(BaseSettings):
       DATABASE_URL: str
       BETTER_AUTH_SECRET: str
       FRONTEND_URL: str = "http://localhost:3000"
       JWT_EXPIRATION_HOURS: int = 24

       class Config:
           env_file = ".env"
           case_sensitive = True

   settings = Settings()
   ```

2. Usage throughout application:
   ```python
   from config import settings

   jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm="HS256")
   ```

3. Startup validation:
   - Pydantic raises `ValidationError` if required env vars missing
   - Application fails fast with clear error message

### Alternatives Considered

- **os.getenv() everywhere**: No type validation, scattered configuration, runtime errors
- **Config file (YAML/JSON)**: Less flexible than env vars, harder for deployment environments

### References

- Pydantic Settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/

---

## 8. API Response Serialization

### Decision

Use **Pydantic v2 models** as FastAPI `response_model` for automatic serialization.

### Rationale

- Pydantic models provide automatic JSON serialization
- FastAPI automatically validates response data against schema
- Type safety for responses (prevents returning wrong data)
- Automatic documentation in OpenAPI schema
- SQLModel models can be used directly as response models (they extend Pydantic BaseModel)

### Implementation Approach

1. Define response schemas in `backend/src/schemas/` directory:
   - `schemas/auth.py`: `AuthResponse`, `UserResponse`
   - `schemas/task.py`: `TaskResponse`, `TaskListResponse`

2. Use `response_model` parameter in route decorators:
   ```python
   @app.post("/api/auth/signup", response_model=AuthResponse, status_code=201)
   async def signup(credentials: SignupRequest):
       ...
       return AuthResponse(token=jwt_token, user=user)
   ```

3. Datetime serialization:
   - Pydantic automatically serializes Python `datetime` objects to ISO 8601 strings
   - Configure `json_encoders` if custom format needed

4. Null handling:
   - Use `Optional[str] = None` for nullable fields like `Task.description`

### Alternatives Considered

- **Manual dict construction**: Error-prone, no validation, no OpenAPI documentation
- **Custom JSON encoder**: Reinventing Pydantic's wheel

### References

- FastAPI response models: https://fastapi.tiangolo.com/tutorial/response-model/

---

## 9. Logging Strategy

### Decision

Use Python's **standard `logging` module** with **structured logging via JSON formatter**.

### Rationale

- Standard library logging is sufficient for Phase II
- Structured JSON logs are machine-readable for log aggregation tools (CloudWatch, Datadog)
- No additional dependencies for basic logging
- FastAPI integrates with standard logging
- Can upgrade to `structlog` later if needed for more advanced features

### Implementation Approach

1. Configure logging in `main.py` startup event:
   ```python
   import logging

   logging.basicConfig(
       level=logging.INFO,
       format='{"time":"%(asctime)s", "level":"%(levelname)s", "message":"%(message)s", "module":"%(name)s"}',
       handlers=[logging.StreamHandler()]  # stdout for container logging
   )
   ```

2. Usage in modules:
   ```python
   import logging

   logger = logging.getLogger(__name__)

   logger.info(f"User {user_id} created task {task_id}")
   logger.error(f"Database connection failed: {error}", exc_info=True)
   ```

3. Log levels:
   - INFO: Successful operations (task created, user logged in)
   - WARNING: Unusual but handled conditions (JWT near expiration)
   - ERROR: Failures requiring attention (database errors, 500 responses)

### Alternatives Considered

- **print() statements**: Not production-ready, no log levels, no structure
- **structlog**: Excellent library but overkill for Phase II, adds dependency

### References

- Python logging: https://docs.python.org/3/library/logging.html
- FastAPI logging: https://fastapi.tiangolo.com/tutorial/middleware/

---

## 10. Testing Strategy (Future)

### Decision

Use **pytest** with **pytest-asyncio** for async test support (planned for post-Phase II).

### Rationale

- pytest is the Python testing standard with rich ecosystem
- pytest-asyncio enables testing async FastAPI routes
- FastAPI provides `TestClient` for easy API testing
- SQLModel supports in-memory SQLite for test databases
- Fixtures enable reusable test data and auth mocking

### Implementation Approach (Future)

1. Test structure:
   ```
   backend/tests/
   ├── unit/          # Unit tests for auth, password hashing, utils
   ├── integration/   # API endpoint tests with test database
   └── conftest.py    # Shared fixtures (test client, test DB, auth tokens)
   ```

2. Key fixtures:
   - `test_client`: FastAPI TestClient with test database
   - `test_user`: Authenticated test user with JWT token
   - `test_tasks`: Sample task data for testing

3. Test coverage goals:
   - Unit tests for JWT validation, password hashing
   - Integration tests for all API endpoints (auth, CRUD)
   - Authorization tests (ensure user isolation)

### Alternatives Considered

- **unittest**: Standard library but less Pythonic than pytest
- **FastAPI's built-in testing without pytest**: Limited features

### References

- Pytest: https://docs.pytest.org/
- FastAPI testing: https://fastapi.tiangolo.com/tutorial/testing/

---

## Summary of Technical Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Web Framework** | FastAPI | Modern async framework, automatic OpenAPI docs, Pydantic integration |
| **ORM** | SQLModel | Combines SQLAlchemy + Pydantic, type-safe, async support |
| **Database** | Neon Serverless PostgreSQL | Managed Postgres, serverless scaling, standard protocol |
| **DB Driver** | asyncpg | Async PostgreSQL driver for non-blocking I/O |
| **JWT Handling** | PyJWT | Standard Python JWT library, simple API |
| **Password Hashing** | Passlib (bcrypt) | Cryptographically secure, industry standard, tunable cost factor |
| **Validation** | Pydantic v2 | Request/response validation, type coercion, JSON serialization |
| **CORS** | FastAPI CORSMiddleware | Built-in, handles preflight, origin whitelisting |
| **Configuration** | Pydantic Settings + python-dotenv | Type-safe env vars, .env loading, validation |
| **Logging** | Standard logging (JSON format) | Built-in, structured logs, container-friendly |
| **Migrations** | SQLModel create_all (Phase II), Alembic (future) | Simple for prototyping, upgrade path to production |
| **Testing** | pytest + pytest-asyncio (future) | Standard Python testing, async support |
| **ASGI Server** | Uvicorn | Fast ASGI server for FastAPI, production-ready |

---

## Implementation Sequencing

Based on research findings, the implementation sequence is:

1. **Configuration & Environment** (config.py, .env setup)
2. **Database Connection** (db.py with SQLModel async engine)
3. **Database Models** (User, Task models with relationships)
4. **Authentication Layer** (JWT verification, password hashing)
5. **Auth Endpoints** (signup, login)
6. **Task CRUD Endpoints** (with user isolation enforcement)
7. **Error Handling** (global exception handlers)
8. **CORS Configuration** (CORSMiddleware setup)
9. **Logging** (structured JSON logging)
10. **Health Check Endpoint** (/health for deployment)

---

## Open Questions / Future Research

None - all technical decisions for Phase II implementation are resolved.

**Note**: Testing infrastructure (pytest setup) is deferred to post-Phase II but research is complete and ready for implementation when prioritized.
