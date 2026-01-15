"""
FastAPI application entry point.
Configures middleware, routers, exception handlers, and startup events.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.db import init_db
from src.routes import auth, tasks, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Startup:
        - Initialize database (create tables if not exist)

    Shutdown:
        - Cleanup resources (if needed)
    """
    # Startup: Initialize database
    await init_db()
    print("✓ Database initialized")

    yield

    # Shutdown: Cleanup (if needed)
    print("✓ Application shutdown")


# Create FastAPI application
app = FastAPI(
    title="Todo Backend API",
    description="REST API for Todo application with JWT authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],  # Frontend origin from environment
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# Global exception handler for Pydantic ValidationError
# Convert 422 Unprocessable Entity → 400 Bad Request for better client UX
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors.

    Converts 422 Unprocessable Entity to 400 Bad Request with detailed error messages.
    """
    errors = exc.errors()
    error_messages = []

    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_messages.append(f"{field}: {message}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "; ".join(error_messages)}
    )


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint for deployment readiness probes.

    Returns:
        200 OK: {"status": "healthy"}
    """
    return {"status": "healthy"}


# Register routers
app.include_router(auth.router)  # /api/auth/signup, /api/auth/login
app.include_router(tasks.router)  # /api/tasks, /api/tasks/:id
app.include_router(chat.router)  # /api/{user_id}/chat


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Todo Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
