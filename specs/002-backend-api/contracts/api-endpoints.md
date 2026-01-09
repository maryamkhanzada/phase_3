# API Endpoint Contracts: Backend Implementation

**Feature**: Backend REST API for Todo Application
**Branch**: `002-backend-api`
**Date**: 2026-01-09
**Phase**: 1 - Design
**Compatibility**: 100% compatible with frontend contracts in `specs/001-frontend-ui/contracts/api-endpoints.md`

## Overview

This document defines the REST API endpoints that the backend MUST implement. These contracts are the source of truth for backend implementation and MUST match frontend expectations exactly.

**Base URL**: Configurable via environment variable (e.g., `http://localhost:8000` in development)
**Authentication**: JWT token via `Authorization: Bearer <token>` header for protected endpoints
**Content-Type**: `application/json` for all requests and responses

---

## Authentication Endpoints

### POST /api/auth/signup

Create a new user account.

**Authentication**: None required (public endpoint)

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Request Validation**:
- `email`: Required, valid email format (RFC 5322), max 255 characters
- `password`: Required, minimum 8 characters

**Success Response** (201 Created):
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
  OR
  ```json
  { "error": "Password must be at least 8 characters" }
  ```

- **409 Conflict**: Email already registered
  ```json
  { "error": "Email already registered" }
  ```

**Backend Implementation Requirements**:
1. Validate email format using Pydantic regex pattern
2. Validate password length ≥ 8 characters
3. Check if email already exists in database (query `User` table by email)
4. Hash password using bcrypt (Passlib) before storing
5. Create new `User` record with hashed password
6. Generate JWT token containing `user_id` and `email` claims with 24-hour expiration
7. Return 201 with token and user object (excluding password_hash)

---

### POST /api/auth/login

Authenticate an existing user.

**Authentication**: None required (public endpoint)

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Request Validation**:
- `email`: Required, valid email format
- `password`: Required

**Success Response** (200 OK):
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

**Backend Implementation Requirements**:
1. Validate email and password are provided
2. Query `User` table by email
3. If user not found → 401 Unauthorized
4. Verify password using bcrypt (Passlib) against stored hash
5. If password incorrect → 401 Unauthorized
6. Generate JWT token containing `user_id` and `email` claims with 24-hour expiration
7. Return 200 with token and user object (excluding password_hash)

**Security Note**: Use generic error message "Invalid email or password" for both email-not-found and password-incorrect cases to prevent user enumeration attacks.

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

**Query Parameters**: None (no pagination in Phase II)

**Success Response** (200 OK):
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

**Backend Implementation Requirements**:
1. Extract and validate JWT token from Authorization header
2. Extract `user_id` from validated token
3. Query `Task` table with `WHERE user_id = <authenticated_user_id>`
4. Order by `created_at DESC` (newest first)
5. Return 200 with task array (empty array if no tasks)
6. Serialize datetimes as ISO 8601 UTC format

**Critical Security**: NEVER return tasks belonging to other users. ALWAYS filter by authenticated `user_id`.

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
  "description": "Milk, eggs, bread"
}
```

**Request Validation**:
- `title`: Required, non-empty after trimming, max 255 characters
- `description`: Optional, max 1000 characters if provided

**Success Response** (201 Created):
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
  OR
  ```json
  { "error": "Title must not exceed 255 characters" }
  ```

- **401 Unauthorized**: Missing or invalid JWT token
  ```json
  { "error": "Unauthorized" }
  ```

**Backend Implementation Requirements**:
1. Extract and validate JWT token
2. Extract `user_id` from validated token
3. Validate request body (title required, non-empty, max lengths)
4. Generate UUID for task `id`
5. Create `Task` record with:
   - `user_id` = authenticated user's ID (from JWT, NOT from request body)
   - `completed` = false
   - `created_at` = current UTC timestamp
   - `updated_at` = current UTC timestamp
6. Return 201 with created task

**Critical Security**: `user_id` MUST come from JWT token, NEVER from client request. This prevents users from creating tasks for other users.

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

**Request Body** (all fields optional, partial update):
```json
{
  "title": "Buy groceries and snacks",
  "description": "Milk, eggs, bread, chips",
  "completed": true
}
```

**Request Validation**:
- `title`: If provided, must be non-empty after trimming, max 255 characters
- `description`: If provided, max 1000 characters (can be set to null explicitly)
- `completed`: If provided, must be boolean

**Success Response** (200 OK):
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

- **404 Not Found**: Task does not exist (or doesn't belong to user)
  ```json
  { "error": "Task not found" }
  ```

**Backend Implementation Requirements**:
1. Extract and validate JWT token
2. Extract `user_id` from validated token
3. Query `Task` table with `WHERE id = :id AND user_id = <authenticated_user_id>`
4. If no task found → 404 Not Found (combined: doesn't exist OR doesn't belong to user)
5. Validate request body fields if provided
6. Update ONLY the fields provided in request (partial update support)
7. Automatically update `updated_at` to current UTC timestamp
8. Return 200 with updated task

**Critical Security**: ALWAYS include `user_id` filter in query. This prevents users from updating other users' tasks.

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

**Success Response** (204 No Content):
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

- **404 Not Found**: Task does not exist (or doesn't belong to user)
  ```json
  { "error": "Task not found" }
  ```

**Backend Implementation Requirements**:
1. Extract and validate JWT token
2. Extract `user_id` from validated token
3. Query `Task` table with `WHERE id = :id AND user_id = <authenticated_user_id>`
4. If no task found → 404 Not Found
5. Delete task from database
6. Return 204 No Content (empty body)

**Critical Security**: ALWAYS include `user_id` filter in delete query. This prevents users from deleting other users' tasks.

---

## Health Check Endpoint

### GET /health

Health check for deployment readiness probes.

**Authentication**: None required (public endpoint)

**Success Response** (200 OK):
```json
{
  "status": "healthy"
}
```

**Backend Implementation Requirements**:
1. Check database connectivity (optional: perform simple query)
2. If database reachable → return 200 with `{"status": "healthy"}`
3. If database unreachable → return 503 Service Unavailable with `{"status": "unhealthy"}`

**Usage**: Used by container orchestration (Kubernetes, ECS) for liveness/readiness probes.

---

## Error Response Format

All errors follow a consistent JSON format:

```json
{
  "error": "Human-readable error message"
}
```

### HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| **200 OK** | Successful GET/PUT request | Task retrieved/updated successfully |
| **201 Created** | Successful POST (resource created) | User/task created |
| **204 No Content** | Successful DELETE | Task deleted (empty response body) |
| **400 Bad Request** | Validation error or malformed request | Invalid email, password too short, title empty |
| **401 Unauthorized** | Missing, invalid, or expired JWT token | No token, invalid signature, expired |
| **403 Forbidden** | Valid token but insufficient permissions | User trying to access another user's task |
| **404 Not Found** | Resource does not exist | Task ID not found (or not owned by user) |
| **409 Conflict** | Resource already exists | Email already registered |
| **500 Internal Server Error** | Unexpected server error | Database crash, unhandled exception |

### Error Handling Best Practices

1. **User Enumeration Prevention**: Use generic messages for auth failures
   - Bad: "Email not found" vs "Password incorrect" (reveals which emails exist)
   - Good: "Invalid email or password" (generic for both cases)

2. **Internal Details**: Never expose stack traces, database errors, or file paths to clients
   - Log detailed errors server-side for debugging
   - Return generic "An error occurred" messages for 500 errors

3. **Validation Errors**: Provide specific, actionable messages for 400 errors
   - Good: "Title must not exceed 255 characters"
   - Bad: "Validation failed"

---

## Authentication Flow

1. **Signup**:
   - User submits email/password → POST /api/auth/signup
   - Backend validates, hashes password, creates user, generates JWT
   - Frontend receives token → stores in localStorage → redirects to /app/tasks

2. **Login**:
   - User submits email/password → POST /api/auth/login
   - Backend validates credentials, generates JWT
   - Frontend receives token → stores in localStorage → redirects to /app/tasks

3. **Authenticated Requests**:
   - Frontend attaches token to every request: `Authorization: Bearer <token>`
   - Backend validates token, extracts user_id, processes request
   - If token invalid/expired → backend returns 401
   - Frontend clears token, redirects to /login

4. **Logout**:
   - Frontend clears token from localStorage
   - No backend call needed (JWT is stateless)

---

## CORS Configuration

Backend MUST configure CORS to allow requests from frontend origin:

```
Access-Control-Allow-Origin: <FRONTEND_URL from env variable>
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Allow-Credentials: true (if needed for cookies)
```

**Development**: `Access-Control-Allow-Origin: http://localhost:3000`
**Production**: `Access-Control-Allow-Origin: https://app.yourdomain.com`

**Note**: NEVER use wildcard `*` for `Access-Control-Allow-Origin` when credentials are involved.

---

## Request/Response Examples

### Example 1: Successful Login Flow

**Request**:
```http
POST /api/auth/login HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "email": "alice@example.com",
  "password": "securepassword123"
}
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNTUwZTg0MDAtZTI5Yi00MWQ0LWE3MTYtNDQ2NjU1NDQwMDAwIiwiZW1haWwiOiJhbGljZUBleGFtcGxlLmNvbSIsImV4cCI6MTczNjQ0ODAwMH0.signature",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "alice@example.com"
  }
}
```

---

### Example 2: Create Task

**Request**:
```http
POST /api/tasks HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Response**:
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "task": {
    "id": "a1b2c3d4-e5f6-4a5b-8c7d-9e0f1a2b3c4d",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2026-01-09T14:30:00Z",
    "updated_at": "2026-01-09T14:30:00Z"
  }
}
```

---

### Example 3: Unauthorized Access (403)

**Request**:
```http
PUT /api/tasks/other-user-task-id HTTP/1.1
Host: localhost:8000
Authorization: Bearer <alice's token>
Content-Type: application/json

{
  "completed": true
}
```

**Response**:
```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "error": "Task not found"
}
```

**Note**: Backend returns 404 instead of 403 to avoid information leakage (doesn't confirm task exists but belongs to another user). Combined authorization + existence check.

---

## Implementation Checklist

Backend implementation is complete when:

- [ ] POST /api/auth/signup endpoint implemented with bcrypt password hashing
- [ ] POST /api/auth/login endpoint implemented with password verification
- [ ] GET /api/tasks endpoint with user_id filtering
- [ ] POST /api/tasks endpoint with user_id from JWT (not client)
- [ ] PUT /api/tasks/:id endpoint with ownership verification
- [ ] DELETE /api/tasks/:id endpoint with ownership verification
- [ ] GET /health endpoint for deployment probes
- [ ] JWT validation dependency/middleware functional
- [ ] All endpoints return correct HTTP status codes
- [ ] All error responses use `{"error": "message"}` format
- [ ] CORS configured for frontend origin
- [ ] Datetime serialization in ISO 8601 UTC format
- [ ] All task queries filter by authenticated user_id
- [ ] No cross-user data leakage possible

---

## Frontend Compatibility Validation

These contracts are **100% compatible** with frontend expectations documented in `specs/001-frontend-ui/contracts/api-endpoints.md`. No discrepancies exist.

**Frontend Integration Readiness**: ✅

When backend implements these contracts exactly as specified, frontend integration will work without modification.
