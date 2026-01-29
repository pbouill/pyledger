from contextlib import asynccontextmanager
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

        from typing import Any

        async def refresh(self, obj: Any) -> None:
            # emulate DB assigning defaults/populating fields after insert
            obj.id = 1
            obj.is_active = True
            obj.is_admin = False

    yield Dummy()


async def test_register_sets_message_header() -> None:
    class DummyConn:
        async def run_sync(self, fn: object) -> None:
            return None

    class DummyEngine:
        @asynccontextmanager
        async def begin(self) -> AsyncGenerator["DummyConn", None]:
            yield DummyConn()

    from typing import cast

    from sqlalchemy.ext.asyncio import AsyncEngine

    import canon.api.auth as auth_mod

    app = create_app(engine=cast(AsyncEngine, DummyEngine()))
    app.dependency_overrides[get_session] = fake_session

    # Prevent passlib/bcrypt backend detection from running in tests by stubbing hash
    def fake_hash(password: str) -> str:
        return "fakehash"

    from typing import Any

    auth_mod.get_password_hash = cast(Any, fake_hash)

    transport = ASGITransport(app=app)
    payload = {"username": "u2", "email": "u2@example.com", "password": "goodpw"}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/auth/register", json=payload)

    assert r.status_code == 200
    assert r.headers.get("X-App-Message") is not None
    assert "registration" in r.headers.get("X-App-Message", "").lower()
