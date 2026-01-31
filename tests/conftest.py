import asyncio
import warnings
from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient
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


# HTTP client for tests that uses an ASGI transport and overrides the
# `get_session` dependency so each request uses a test sessionmaker bound
# to the shared test engine. This keeps request handling consistent and
# avoids boilerplate in individual tests.
@pytest.fixture
async def async_client(engine: AsyncEngine) -> AsyncGenerator["AsyncClient", None]:
    from httpx import AsyncClient
    from httpx._transports.asgi import ASGITransport

    from canon.app import create_app
    from canon.db import get_session

    app = create_app(engine=engine)
    session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

    async def _get_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_maker() as s:
            yield s

    app.dependency_overrides[get_session] = _get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_username() -> str:
    return "testuser"


@pytest.fixture
def test_email() -> str:
    return "test@example.com"


@pytest.fixture
def test_password() -> str:
    return "hunter2"


@pytest.fixture
async def token(
    async_client: AsyncClient,
    test_username: str,
    test_email: str,
    test_password: str,
) -> str:
    """Register a test user and return a bearer token string."""
    r = await async_client.post(
        "/api/auth/register",
        json={
            "username": test_username,
            "email": test_email,
            "password": test_password,
        },
    )
    # Allow registration to be idempotent in tests
    if r.status_code not in (200, 400):
        r.raise_for_status()
    lr = await async_client.post(
        "/api/auth/login",
        data={"username": test_username, "password": test_password},
    )
    lr.raise_for_status()
    return lr.json().get("access_token")


@pytest.fixture
def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}