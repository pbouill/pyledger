


"""
(engine-per-tenant) easier later.
"""



from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .config import get_database_url

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None

# For sync DB session (for FastAPI dependencies that expect sync Session)


def get_engine() -> AsyncEngine:
    global _engine, _sessionmaker
    if _engine is None:
        DATABASE_URL = get_database_url()
        # Use asyncpg driver
        async_database_url = DATABASE_URL.replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        _engine = create_async_engine(async_database_url)
        _sessionmaker = async_sessionmaker(_engine, expire_on_commit=False)
    return _engine


def set_engine(engine: AsyncEngine) -> None:
    """Set the global engine and sessionmaker (useful for tests).

    When tests create an in-memory engine they can call this (via the
    application factory) so that request handlers which call
    `get_session()` directly (instead of via dependency injection)
    use the test engine's sessionmaker.
    """
    global _engine, _sessionmaker
    _engine = engine
    _sessionmaker = async_sessionmaker(_engine, expire_on_commit=False)




async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields an AsyncSession for request handlers."""
    global _sessionmaker
    if _sessionmaker is None:
        # Ensure engine/sessionmaker initialized
        get_engine()
    # mypy: convince the type checker that _sessionmaker is initialized
    assert _sessionmaker is not None
    async with _sessionmaker() as session:
        yield session
