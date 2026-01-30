import asyncio
import warnings
from typing import AsyncGenerator, Generator

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from canon.migration import migrate_database

# Suppress deprecation warnings emitted by argon2 when libraries access
# `argon2.__version__` directly. Prefer upstream fix; in tests silence this
# known, benign warning.
warnings.filterwarnings(
    "ignore",
    message="Accessing argon2.__version__ is deprecated",
    category=DeprecationWarning,
)
# Also ignore deprecation warnings originating from passlib's handler
# which probes argon2.__version__ during handler initialization.
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module=r"passlib\.handlers\.argon2",
)




@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True, future=True)
    await migrate_database(engine)
    yield engine
    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        yield session