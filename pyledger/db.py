"""Database helpers: engine and async session dependency.

This is intentionally minimal for single-tenant usage, and includes small abstractions
(Async engine factory and session dependency) that will make moving to multi-tenant
(engine-per-tenant) easier later.
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker

from .config import get_database_url


_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global _engine, _sessionmaker
    if _engine is None:
        DATABASE_URL = get_database_url()
        # Use asyncpg driver
        _engine = create_async_engine(DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"))
        _sessionmaker = async_sessionmaker(_engine, expire_on_commit=False)
    return _engine


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields an AsyncSession for request handlers."""
    global _sessionmaker
    if _sessionmaker is None:
        # Ensure engine/sessionmaker initialized
        get_engine()
    async with _sessionmaker() as session:
        yield session
