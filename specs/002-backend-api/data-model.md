# Data Model: Backend Database Schema

**Feature**: Backend REST API for Todo Application
**Branch**: `002-backend-api`
**Date**: 2026-01-09
**Phase**: 1 - Design

## Overview

This document defines the database schema for the backend using SQL Model concepts. All models are implemented as SQLModel classes that combine SQLAlchemy ORM capabilities with Pydantic validation.

**Database**: Neon Serverless PostgreSQL
**ORM**: SQLModel (SQLAlchemy + Pydantic)
**Driver**: asyncpg (async PostgreSQL adapter)

---

## Entity: User

### Purpose

Represents a registered user account. Users own tasks and authenticate via JWT tokens.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Unique user identifier (auto-generated UUID v4) |
| `email` | String(255) | UNIQUE, NOT NULL | User's email address (used for login) |
| `password_hash` | String(255) | NOT NULL | Bcrypt-hashed password (never store plaintext) |
| `created_at` | DateTime (UTC) | NOT NULL, DEFAULT NOW() | Account creation timestamp |

### Indexes

- **Primary Key**: `id` (auto-indexed)
- **Unique Index**: `email` (enforces uniqueness, enables fast lookup by email)

### Relationships

- **One-to-Many** → `Task`: A user owns zero or more tasks
  - Foreign key: `Task.user_id` references `User.id`
  - Cascade behavior: If user deleted, cascade delete all tasks (future consideration)

### Validation Rules

- **Email**: Must match RFC 5322 email format (validated by Pydantic)
- **Password**: Minimum 8 characters (validated before hashing, hash stored in `password_hash`)
- **Created_at**: Automatically set to current UTC timestamp on insert

### Usage Notes

- User records are created via `/api/auth/signup` endpoint
- User authentication occurs via `/api/auth/login` endpoint
- `password_hash` field is NEVER returned in API responses (excluded from Pydantic response models)
- `id` field is used as `user_id` in JWT tokens for authentication

### SQLModel Declaration Pattern

```python
class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, max_length=255, index=True)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationship (not a database column)
    tasks: List["Task"] = Relationship(back_populates="owner")
```

---

## Entity: Task

### Purpose

Represents a todo item owned by a user. Tasks support title, description, and completion status.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Unique task identifier (auto-generated UUID v4) |
| `title` | String(255) | NOT NULL | Task title (required, user-facing) |
| `description` | Text | NULL | Optional task description (can be null or empty) |
| `completed` | Boolean | NOT NULL, DEFAULT FALSE | Task completion status |
| `user_id` | UUID | FOREIGN KEY (User.id), NOT NULL | Owner user identifier |
| `created_at` | DateTime (UTC) | NOT NULL, DEFAULT NOW() | Task creation timestamp |
| `updated_at` | DateTime (UTC) | NOT NULL, DEFAULT NOW() | Last update timestamp (auto-updated) |

### Indexes

- **Primary Key**: `id` (auto-indexed)
- **Foreign Key Index**: `user_id` (critical for user isolation queries)
  - Enables fast filtering: `SELECT * FROM tasks WHERE user_id = ?`

### Relationships

- **Many-to-One** → `User`: Each task belongs to exactly one user
  - Foreign key: `user_id` references `User.id`
  - Cascade behavior: Enforce referential integrity (user must exist)

### Validation Rules

- **Title**: Non-empty after trimming whitespace, max 255 characters (Pydantic validation)
- **Description**: Optional, max 1000 characters if provided (Pydantic validation)
- **Completed**: Boolean (true/false), defaults to false on creation
- **user_id**: Must reference existing User.id (foreign key constraint)
- **updated_at**: Automatically updated to current UTC timestamp on any field modification

### Usage Notes

- Tasks are filtered by `user_id` in ALL queries to enforce user isolation
- `user_id` is ALWAYS extracted from validated JWT token, NEVER from client request
- Task ownership is checked before update/delete operations (403 if mismatch)
- `description` can be `null` (database NULL, serialized as JSON `null`)

### SQLModel Declaration Pattern

```python
class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationship (not a database column)
    owner: User = Relationship(back_populates="tasks")
```

---

## Schema Diagram

```
┌─────────────────────────────────┐
│          User                   │
├─────────────────────────────────┤
│ id (UUID) PK                    │
│ email (String) UNIQUE           │
│ password_hash (String)          │
│ created_at (DateTime)           │
└─────────────────────────────────┘
                │
                │ 1:N
                │
                ▼
┌─────────────────────────────────┐
│          Task                   │
├─────────────────────────────────┤
│ id (UUID) PK                    │
│ title (String)                  │
│ description (Text, nullable)    │
│ completed (Boolean)             │
│ user_id (UUID) FK               │◄── References User.id
│ created_at (DateTime)           │
│ updated_at (DateTime)           │
└─────────────────────────────────┘
```

---

## Database Constraints

### Foreign Key Constraints

- **Task.user_id → User.id**
  - ON DELETE: Not specified in Phase II (manual handling if user deletion implemented)
  - ON UPDATE: CASCADE (if user.id changes, update task.user_id - unlikely with UUIDs)

### Unique Constraints

- **User.email**: UNIQUE (prevents duplicate email registrations)

### Check Constraints (Future Consideration)

- **Task.title**: `LENGTH(TRIM(title)) > 0` (enforce non-empty titles at database level)
- Currently handled by Pydantic validation; database constraint optional for defense-in-depth

---

## Data Isolation Enforcement

### Query Patterns

All task queries MUST include `WHERE user_id = <authenticated_user_id>` filter:

**Correct (Enforces Isolation):**
```sql
SELECT * FROM tasks WHERE user_id = '550e8400-e29b-41d4-a716-446655440000';
SELECT * FROM tasks WHERE id = 'task-uuid' AND user_id = '550e8400...';
```

**INCORRECT (Security Vulnerability):**
```sql
SELECT * FROM tasks WHERE id = 'task-uuid';  -- Missing user_id check!
SELECT * FROM tasks;  -- Returns ALL users' tasks!
```

### Authorization Checks

Before UPDATE or DELETE operations:

1. Fetch task by `id` and `user_id` (composite filter)
2. If no rows returned → 404 Not Found (task doesn't exist OR doesn't belong to user)
3. If row returned → proceed with operation

**Never separate fetch and authorization check** - use single query with both filters.

---

## Timestamps & Timezone Handling

### Timezone Policy

- **Storage**: All timestamps stored in UTC (database-level `TIMESTAMP WITH TIME ZONE`)
- **Serialization**: ISO 8601 format with explicit UTC timezone: `2026-01-09T10:30:00Z`
- **Client Handling**: Frontend converts to user's local timezone for display

### Auto-Update Behavior

**created_at**:
- Set once on INSERT
- Never modified on UPDATE

**updated_at**:
- Set on INSERT (same as created_at)
- Automatically updated on UPDATE via:
  - SQLModel `onupdate` parameter (application-level)
  - OR PostgreSQL trigger (database-level, more reliable)

**Recommended**: Use PostgreSQL trigger for `updated_at` to ensure consistency even with direct database modifications:

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_task_updated_at
BEFORE UPDATE ON tasks
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

---

## Migration Strategy (Phase II)

### Initial Schema Creation

Use SQLModel's `create_all()` method on application startup:

```python
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

This creates:
1. `users` table with all fields and indexes
2. `tasks` table with all fields, indexes, and foreign keys

### Schema Changes (Development)

For Phase II (hackathon/prototype):
- Drop database and recreate: `DROP DATABASE todo_app; CREATE DATABASE todo_app;`
- Re-run `create_all()` to recreate schema

**WARNING**: This destroys all data. Acceptable for development, NOT for production.

### Future: Alembic Migrations

When moving to production:
1. Generate initial migration: `alembic revision --autogenerate -m "Initial schema"`
2. Apply migrations: `alembic upgrade head`
3. Future schema changes: Modify SQLModel → `alembic revision --autogenerate` → `alembic upgrade head`

---

## Pydantic Response Models

### User Response (Public)

Returned in API responses (excludes password_hash):

```python
class UserResponse(BaseModel):
    id: UUID
    email: str
```

### Task Response (Public)

Returned in API responses:

```python
class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    completed: bool
    user_id: UUID
    created_at: datetime
    updated_at: datetime
```

### Request Models

**SignupRequest / LoginRequest:**
```python
class AuthRequest(BaseModel):
    email: str = Field(..., max_length=255, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    password: str = Field(..., min_length=8)
```

**TaskCreateRequest:**
```python
class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
```

**TaskUpdateRequest:**
```python
class TaskUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
```

---

## Data Validation Summary

| Validation | Layer | Enforced By |
|-----------|-------|-------------|
| Email format | Application | Pydantic regex pattern |
| Password length (≥8 chars) | Application | Pydantic Field constraint |
| Title non-empty | Application | Pydantic min_length=1 |
| Title max length (255) | Application + Database | Pydantic + VARCHAR(255) |
| Description max length (1000) | Application | Pydantic (database TEXT has no limit) |
| Email uniqueness | Database | UNIQUE constraint on User.email |
| Foreign key validity | Database | FOREIGN KEY constraint Task.user_id → User.id |
| UUID format | Application | UUID type validation |
| Datetime format | Application | Pydantic datetime type |

**Defense-in-Depth**: Validation at both application (Pydantic) and database (constraints) layers provides redundancy.

---

## Performance Considerations

### Query Performance

**Indexes critical for performance:**
1. `User.email` (UNIQUE index) - Fast login lookup by email
2. `Task.user_id` (INDEX) - Fast filtering of tasks by user (most common query)

**Query patterns:**
- List tasks: `WHERE user_id = ? ORDER BY created_at DESC` (uses index)
- Get task: `WHERE id = ? AND user_id = ?` (composite filter, uses PK + index)

### Connection Pooling

- SQLAlchemy async engine maintains connection pool (default 5 connections)
- Neon Serverless PostgreSQL supports up to 50 concurrent connections per project
- Connection recycling every 3600 seconds to prevent stale connections

### Future Optimizations (If Needed)

- **Pagination**: Add LIMIT/OFFSET to task list queries if users have >100 tasks
- **Caching**: Cache user email→id lookup (login queries) with Redis
- **Read Replicas**: Use Neon read replicas for GET /api/tasks if read-heavy workload

---

## Security Notes

### Password Security

- **NEVER** store plaintext passwords
- **ALWAYS** hash with bcrypt (cost factor 12) before storing in `password_hash`
- **NEVER** return `password_hash` in API responses (exclude from Pydantic models)

### User Isolation

- **ALWAYS** filter by `user_id` from validated JWT token
- **NEVER** trust `user_id` from client request (URL params, request body)
- **ALWAYS** check task ownership before UPDATE/DELETE (403 if mismatch)

### SQL Injection Prevention

- **ALWAYS** use SQLModel parameterized queries (ORM prevents injection)
- **NEVER** construct raw SQL with string concatenation

---

## Summary

- **2 Core Entities**: User, Task
- **1 Relationship**: User (1) → Task (N)
- **3 Indexes**: User.id (PK), User.email (UNIQUE), Task.user_id (FK)
- **UUID Primary Keys**: All entities use UUID v4 for IDs
- **UTC Timestamps**: All datetime fields stored in UTC
- **Type Safety**: SQLModel provides Pydantic validation + SQLAlchemy ORM
- **User Isolation**: Enforced via `user_id` foreign key and query filtering
