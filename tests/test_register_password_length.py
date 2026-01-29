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


async def test_register_password_too_long_returns_400() -> None:
    # Provide a fake engine so app startup doesn't attempt to connect to a real DB
    from contextlib import asynccontextmanager
    from typing import cast

    from sqlalchemy.ext.asyncio import AsyncEngine

    class DummyConn:
        async def run_sync(self, fn: object) -> None:
            return None

    class DummyEngine:
        @asynccontextmanager
        async def begin(self) -> AsyncGenerator["DummyConn", None]:
            yield DummyConn()

    app = create_app(engine=cast(AsyncEngine, DummyEngine()))
    app.dependency_overrides[get_session] = fake_session
    transport = ASGITransport(app=app)
    long_password = "p" * 100  # longer than bcrypt 72-byte limit
    payload = {"username": "u1", "email": "u1@example.com", "password": long_password}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/auth/register", json=payload)
    assert r.status_code == 400
    assert "too long" in r.json().get("detail", "").lower()
