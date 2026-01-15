# Backend REST API - Todo Application

FastAPI-based backend API providing authentication and task management for the Todo application.

## Prerequisites

- Python 3.11+
- PostgreSQL database (Neon Serverless PostgreSQL recommended)
- Git

## Quick Start

### 1. Clone and Navigate

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:
- `DATABASE_URL`: Your Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET`: Shared secret for JWT signing (must match frontend)
- `FRONTEND_URL`: Frontend origin for CORS (default: http://localhost:3000)

### 5. Run Development Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Project Structure

```
backend/
├── src/
│   ├── main.py           # FastAPI application entry point
│   ├── config.py         # Configuration management
│   ├── db.py             # Database connection and session
│   ├── models.py         # SQLModel database models
│   ├── exceptions.py     # Custom exception classes
│   ├── auth/
│   │   ├── jwt.py        # JWT verification and dependencies
│   │   └── password.py   # Password hashing utilities
│   ├── routes/
│   │   ├── auth.py       # Authentication endpoints
│   │   └── tasks.py      # Task CRUD endpoints
│   └── schemas/
│       ├── auth.py       # Auth request/response schemas
│       └── task.py       # Task request/response schemas
├── tests/                # Test suite
├── .env                  # Environment variables (not in git)
├── .env.example          # Environment template
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/login` - Authenticate and receive JWT token

### Tasks (Authenticated)
- `GET /api/tasks` - Fetch all tasks for authenticated user
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/:id` - Update existing task
- `DELETE /api/tasks/:id` - Delete task

### AI Chatbot (Authenticated)
- `POST /api/{user_id}/chat` - Send message to AI chatbot for natural language task management

### System
- `GET /health` - Health check endpoint

## AI Chatbot Features

The backend includes an AI-powered chatbot that allows users to manage tasks through natural language. It uses:

- **Cohere API** for intent classification and entity extraction
- **Three-agent architecture**:
  - **Todo-Orchestrator**: Main brain for intent classification and response generation
  - **Task-Ops-Executor**: Executes MCP tools for task operations (CRUD)
  - **Conversation-Memory**: Manages conversation state with database persistence

### Supported Commands

- **Add tasks**: "Add a task to buy groceries"
- **List tasks**: "Show me my tasks"
- **Update tasks**: "Update task 3 title to review code"
- **Complete tasks**: "Mark task 5 as done"
- **Delete tasks**: "Delete task 7"

### Setup Cohere API

1. Sign up at [Cohere Dashboard](https://dashboard.cohere.com/)
2. Create an API key
3. Add to `.env`:
   ```
   COHERE_API_KEY=your-cohere-api-key-here
   ```

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black src/

# Type checking
mypy src/
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Yes | - | JWT signing secret (min 32 chars) |
| `FRONTEND_URL` | Yes | http://localhost:3000 | Frontend origin for CORS |
| `JWT_EXPIRATION_HOURS` | No | 24 | JWT token expiration time |
| `APP_ENV` | No | development | Application environment |
| `LOG_LEVEL` | No | INFO | Logging level |
| `COHERE_API_KEY` | Yes | - | Cohere API key for AI chatbot NLP |

## Security Notes

- JWT tokens are signed with HS256 algorithm
- Passwords are hashed with bcrypt (cost factor 12)
- All task endpoints enforce user isolation
- CORS is configured for frontend origin only
- No credentials are logged or exposed in responses

## Troubleshooting

### Database Connection Error

**Error**: `asyncpg.exceptions.InvalidCatalogNameError`

**Solution**: Verify `DATABASE_URL` in `.env` and ensure database exists in Neon dashboard.

### JWT Decode Error

**Error**: `jwt.exceptions.DecodeError`

**Solution**: Ensure `BETTER_AUTH_SECRET` matches between frontend and backend.

### CORS Error

**Error**: `Access-Control-Allow-Origin header not present`

**Solution**: Verify `FRONTEND_URL` in `.env` matches your frontend origin.

### Import Errors

**Error**: `ModuleNotFoundError`

**Solution**: Activate virtual environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (macOS/Linux)

## License

MIT
