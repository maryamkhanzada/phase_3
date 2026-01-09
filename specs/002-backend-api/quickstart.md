# Quick Start Guide: Backend Development

**Feature**: Backend REST API for Todo Application
**Branch**: `002-backend-api`
**Date**: 2026-01-09

## Prerequisites

- Python 3.11+
- PostgreSQL access (Neon Serverless PostgreSQL account)
- Git
- Code editor (VS Code recommended)

## Initial Setup (5 minutes)

### 1. Create Backend Directory

```bash
mkdir backend
cd backend
```

### 2. Initialize Python Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

Create `requirements.txt`:
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.14
asyncpg==0.29.0
pyjwt==2.8.0
passlib[bcrypt]==1.7.4
pydantic-settings==2.1.0
python-dotenv==1.0.0
```

Install:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create `.env` file in `backend/` directory:
```env
DATABASE_URL=postgresql://user:password@host:5432/todo_db
BETTER_AUTH_SECRET=your-shared-secret-here
FRONTEND_URL=http://localhost:3000
JWT_EXPIRATION_HOURS=24
```

**Get DATABASE_URL from Neon:**
1. Log in to https://neon.tech
2. Create new project: "todo-app"
3. Copy connection string (format: `postgresql://user:password@host/dbname`)

**BETTER_AUTH_SECRET:**
- Must match the secret used by Better Auth on frontend
- Generate strong random string: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

## Project Structure

```
backend/
├── src/
│   ├── main.py          # FastAPI app entry point
│   ├── config.py        # Environment configuration
│   ├── db.py            # Database connection
│   ├── models.py        # SQLModel database models
│   ├── auth/
│   │   ├── jwt.py       # JWT verification
│   │   └── password.py  # Password hashing
│   ├── routes/
│   │   ├── auth.py      # Auth endpoints (signup, login)
│   │   └── tasks.py     # Task CRUD endpoints
│   ├── schemas/
│   │   ├── auth.py      # Auth request/response models
│   │   └── task.py      # Task request/response models
│   └── exceptions.py    # Custom exception classes
├── tests/               # Future: pytest test suite
├── .env                 # Environment variables (DO NOT COMMIT)
├── .gitignore           # Git ignore file
└── requirements.txt     # Python dependencies
```

## Development Workflow

### Step 1: Create Configuration Module

**File**: `src/config.py`

Load and validate environment variables using Pydantic Settings.

### Step 2: Create Database Connection

**File**: `src/db.py`

Set up async SQLAlchemy engine and session dependency.

### Step 3: Define Database Models

**File**: `src/models.py`

Create SQLModel classes for `User` and `Task` entities.

### Step 4: Implement Authentication Layer

**Files**: `src/auth/jwt.py`, `src/auth/password.py`

- JWT verification dependency for protected routes
- Password hashing and verification functions

### Step 5: Implement Auth Endpoints

**File**: `src/routes/auth.py`

- POST /api/auth/signup
- POST /api/auth/login

### Step 6: Implement Task CRUD Endpoints

**File**: `src/routes/tasks.py`

- GET /api/tasks
- POST /api/tasks
- PUT /api/tasks/:id
- DELETE /api/tasks/:id

### Step 7: Configure FastAPI App

**File**: `src/main.py`

- Initialize FastAPI app
- Add CORS middleware
- Register route routers
- Add global exception handlers
- Add health check endpoint

### Step 8: Run Development Server

```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Access:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs (Swagger UI)
- Alternative docs: http://localhost:8000/redoc

## Testing the API

### Using FastAPI Swagger UI

1. Open http://localhost:8000/docs
2. Click "POST /api/auth/signup"
3. Click "Try it out"
4. Enter email and password
5. Click "Execute"
6. Copy the token from response

### Using curl

**Signup**:
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

**Login**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

**Create Task** (replace TOKEN):
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries","description":"Milk, eggs, bread"}'
```

**Get Tasks** (replace TOKEN):
```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer TOKEN"
```

## Common Issues & Solutions

### Issue: Database Connection Error

**Error**: `asyncpg.exceptions.InvalidCatalogNameError: database "todo_db" does not exist`

**Solution**: Create database in Neon dashboard or use connection string with existing database.

### Issue: JWT Decode Error

**Error**: `jwt.exceptions.DecodeError: Invalid token`

**Solution**: Ensure BETTER_AUTH_SECRET matches between frontend and backend.

### Issue: CORS Error in Browser

**Error**: `Access-Control-Allow-Origin header not present`

**Solution**: Verify FRONTEND_URL in .env matches frontend origin (http://localhost:3000).

### Issue: Import Errors

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: Activate virtual environment: `source venv/bin/activate`

## Next Steps

1. Implement all endpoints following contracts in `contracts/api-endpoints.md`
2. Test each endpoint using Swagger UI or curl
3. Verify user isolation (test with multiple users)
4. Test frontend integration
5. Add error handling for edge cases
6. Write automated tests (optional for Phase II)

## Useful Commands

**Activate virtual environment**:
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

**Run development server**:
```bash
uvicorn src.main:app --reload --port 8000
```

**Freeze dependencies**:
```bash
pip freeze > requirements.txt
```

**Database reset** (development only):
```bash
# Drop and recreate database in Neon dashboard
# Then restart backend to run create_all()
```

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangelo.com/)
- [Neon Documentation](https://neon.tech/docs)
- [Backend Spec](./spec.md)
- [API Contracts](./contracts/api-endpoints.md)
- [Data Model](./data-model.md)
