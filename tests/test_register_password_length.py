from typing import AsyncGenerator

from httpx import ASGITransport, AsyncClient

from canon.app import create_app
from canon.db import get_session


async def fake_session() -> AsyncGenerator[object, None]:
    class DummyResult:
        def first(self) -> None:
            return None

    class Dummy:
        async def execute(self, *args: object, **kwargs: object) -> object:
            return DummyResult()

        def add(self, obj: object) -> None:
            pass

        async def commit(self) -> None:
            pass

        async def refresh(self, obj: object) -> None:
            pass

    yield Dummy()


async def test_register_accepts_long_password() -> None:
    """Registration should accept passwords longer than 72 bytes when using Argon2."""
    # Use a real in-memory SQLite engine so the app performs migrations and we
    # exercise the real hashing and DB commit path.
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    app = create_app(engine=engine)

    # Acquire a dedicated connection for this test and create tables there
    conn = await engine.connect()
    try:
        from canon.models import Base

        await conn.run_sync(Base.metadata.create_all)

        # Override get_session to use a sessionmaker that binds to the shared
        # connection so all handler sessions see the same DB state.
        from typing import AsyncGenerator

        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

        session_maker = async_sessionmaker(bind=conn, expire_on_commit=False)

        async def _get_session() -> AsyncGenerator[AsyncSession, None]:
            async with session_maker() as s:
                yield s

        app.dependency_overrides[get_session] = _get_session

        long_password = "p" * 100  # longer than bcrypt 72-byte limit
        payload = {
            "username": "u1",
            "email": "u1@example.com",
            "password": long_password,
        }

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            r = await ac.post("/api/auth/register", json=payload)
            assert r.status_code == 200
            data = r.json()
            assert data.get("username") == "u1"
            # The response headers should include our toast message header
            assert "x-app-message" in r.headers
            assert "registration successful" in (
                r.headers.get("x-app-message", "")
            ).lower()
    finally:
        await conn.close()