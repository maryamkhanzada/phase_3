"""
Database connection and session management.
Uses async SQLAlchemy engine with asyncpg driver for PostgreSQL.
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.config import settings


# Create async engine
# Replace postgresql:// with postgresql+asyncpg:// for async support (if using PostgreSQL)
database_url = settings.database_url
if database_url.startswith("postgresql://") or database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgresql://", "postgresql+asyncpg://"
    ).replace(
        "postgres://", "postgresql+asyncpg://"  # Handle Neon's postgres:// prefix
    )

# Create engine with appropriate settings
engine_kwargs = {
    "echo": settings.app_env == "development",
}

# SQLite-specific connection arguments
if database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_async_engine(database_url, **engine_kwargs)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Initialize database by creating all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    """
    FastAPI dependency that provides a database session.

    Usage:
        @router.get("/endpoint")
        async def endpoint(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with async_session() as session:
        yield session
