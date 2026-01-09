# API Contracts: Assumed Backend REST Endpoints

**Feature**: Frontend UI for Todo Application
**Date**: 2026-01-07
**Status**: Complete (Backend implementation out of scope)

## Overview

This document defines the REST API contract that the frontend assumes exists. These endpoints are implemented by the backend (out of scope for this frontend plan) and documented here for frontend reference.

**Base URL**: Configurable via `NEXT_PUBLIC_API_URL` environment variable (e.g., `http://localhost:8000`)

**Authentication**: Most endpoints require JWT token via `Authorization: Bearer <token>` header.

---

## Authentication Endpoints

### POST /api/auth/signup

Create a new user account.

**Authentication**: None required

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Success Response (201 Created)**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com"
  }
}
```

**Error Responses**:
- **400 Bad Request**: Invalid email format or password too short
  ```json
  { "error": "Invalid email format" }
  ```
- **409 Conflict**: Email already registered
  ```json
  { "error": "Email already registered" }
  ```

**Frontend Usage**:
- Store `token` in localStorage
- Store `user` data in app state
- Redirect to `/app/tasks` after successful signup

---

### POST /api/auth/login

Authenticate an existing user.

**Authentication**: None required

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Success Response (200 OK)**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com"
  }
}
```

**Error Responses**:
- **400 Bad Request**: Missing or invalid fields
  ```json
  { "error": "Email and password required" }
  ```
- **401 Unauthorized**: Invalid credentials
  ```json
  { "error": "Invalid email or password" }
  ```

**Frontend Usage**:
- Store `token` in localStorage
- Store `user` data in app state
- Redirect to `/app/tasks` after successful login

---

## Task Endpoints

All task endpoints require authentication via `Authorization: Bearer <token>` header.

### GET /api/tasks

Fetch all tasks for the authenticated user.

**Authentication**: Required (JWT token)

**Request Headers**:
```
Authorization: Bearer <token>
```

**Query Parameters**: None

**Success Response (200 OK)**:
```json
{
  "tasks": [
    {
      "id": "task-uuid-1",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "user_id": "user-uuid",
      "created_at": "2026-01-07T10:30:00Z",
      "updated_at": "2026-01-07T10:30:00Z"
    },
    {
      "id": "task-uuid-2",
      "title": "Finish project",
      "description": null,
      "completed": true,
      "user_id": "user-uuid",
      "created_at": "2026-01-06T08:15:00Z",
      "updated_at": "2026-01-07T12:45:00Z"
    }
  ]
}
```

**Error Responses**:
- **401 Unauthorized**: Missing or invalid JWT token
  ```json
  { "error": "Unauthorized" }
  ```

**Frontend Usage**:
- Fetch on `/app/tasks` page load
- Display task list to user
- Refetch after create/update/delete operations

---

### POST /api/tasks

Create a new task for the authenticated user.

**Authentication**: Required (JWT token)

**Request Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"  // Optional
}
```

**Success Response (201 Created)**:
```json
{
  "task": {
    "id": "task-uuid-new",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "user_id": "user-uuid",
    "created_at": "2026-01-07T14:20:00Z",
    "updated_at": "2026-01-07T14:20:00Z"
  }
}
```

**Error Responses**:
- **400 Bad Request**: Missing title or validation failure
  ```json
  { "error": "Title is required" }
  ```
- **401 Unauthorized**: Missing or invalid JWT token
  ```json
  { "error": "Unauthorized" }
  ```

**Frontend Usage**:
- Submit from `/app/tasks/new` page
- Add returned task to local task list (optimistic update)
- Redirect to `/app/tasks` after success

---

### PUT /api/tasks/:id

Update an existing task (title, description, or completion status).

**Authentication**: Required (JWT token)

**Request Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**URL Parameters**:
- `id`: Task UUID

**Request Body** (all fields optional, send only what changed):
```json
{
  "title": "Buy groceries and snacks",
  "description": "Milk, eggs, bread, chips",
  "completed": true
}
```

**Success Response (200 OK)**:
```json
{
  "task": {
    "id": "task-uuid-1",
    "title": "Buy groceries and snacks",
    "description": "Milk, eggs, bread, chips",
    "completed": true,
    "user_id": "user-uuid",
    "created_at": "2026-01-07T10:30:00Z",
    "updated_at": "2026-01-07T15:10:00Z"
  }
}
```

**Error Responses**:
- **400 Bad Request**: Validation failure (e.g., empty title)
  ```json
  { "error": "Title cannot be empty" }
  ```
- **401 Unauthorized**: Missing or invalid JWT token
  ```json
  { "error": "Unauthorized" }
  ```
- **403 Forbidden**: Task belongs to different user
  ```json
  { "error": "Access denied" }
  ```
- **404 Not Found**: Task does not exist
  ```json
  { "error": "Task not found" }
  ```

**Frontend Usage**:
- Submit from `/app/tasks/[id]/edit` page for title/description updates
- Submit from task toggle button for completion status changes
- Update local task list with returned task data
- Handle 404 gracefully (task may have been deleted in another session)

---

### DELETE /api/tasks/:id

Delete a task permanently.

**Authentication**: Required (JWT token)

**Request Headers**:
```
Authorization: Bearer <token>
```

**URL Parameters**:
- `id`: Task UUID

**Success Response (204 No Content)**:
- Empty response body

**Error Responses**:
- **401 Unauthorized**: Missing or invalid JWT token
  ```json
  { "error": "Unauthorized" }
  ```
- **403 Forbidden**: Task belongs to different user
  ```json
  { "error": "Access denied" }
  ```
- **404 Not Found**: Task does not exist
  ```json
  { "error": "Task not found" }
  ```

**Frontend Usage**:
- Submit after user confirms deletion in modal
- Remove task from local task list immediately (optimistic update)
- Handle 404 gracefully (task may have been deleted already)

---

## Error Response Format

All errors follow a consistent JSON format:

```json
{
  "error": "Human-readable error message"
}
```

**HTTP Status Codes**:
- **200 OK**: Successful GET/PUT request
- **201 Created**: Successful POST (resource created)
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Validation error or malformed request
- **401 Unauthorized**: Missing, invalid, or expired JWT token
- **403 Forbidden**: Valid token but insufficient permissions (user doesn't own resource)
- **404 Not Found**: Resource does not exist
- **500 Internal Server Error**: Unexpected server error

---

## Authentication Flow

1. User signs up or logs in via `/api/auth/signup` or `/api/auth/login`
2. Backend returns JWT token and user data
3. Frontend stores token in localStorage
4. Frontend attaches token to all subsequent requests: `Authorization: Bearer <token>`
5. Backend validates token and extracts `user_id` for data isolation
6. If token is invalid/expired, backend returns 401
7. Frontend clears token and redirects to `/login`

---

## Data Isolation

- All task endpoints filter by authenticated `user_id` extracted from JWT
- Users can only see/modify their own tasks
- Attempting to access another user's task returns 403 Forbidden
- No `user_id` parameter in requests - always derived from JWT on backend

---

## CORS Configuration (Backend)

Backend must configure CORS to allow frontend origin:

```
Access-Control-Allow-Origin: http://localhost:3000 (development)
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Allow-Credentials: true
```

**Frontend Usage**: No special configuration needed, browser handles CORS automatically.

---

## Notes

- All timestamps in ISO 8601 format (UTC): `2026-01-07T10:30:00Z`
- All IDs are UUIDs (version 4)
- `description` field can be `null` (omitted) or string
- Backend enforces all validation, authorization, and data isolation
- Frontend validates client-side for UX only (backend is source of truth)
- No pagination in Phase II (assumes <100 tasks per user)
- No sorting/filtering in Phase II (frontend displays in returned order)
