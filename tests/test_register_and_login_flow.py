from httpx import ASGITransport, AsyncClient

from canon.app import create_app
from canon.db import get_session


async def test_register_then_login() -> None:
    from sqlalchemy.ext.asyncio import create_async_engine
    # Create a single shared connection and bind sessionmaker to it so all
    # test sessions see the same database state deterministically.
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    app = create_app(engine=engine)

    # Acquire a dedicated connection that lives for the duration of this test
    conn = await engine.connect()
    try:
        # Create tables on that connection
        from canon.models import Base

        await conn.run_sync(Base.metadata.create_all)

        from typing import AsyncGenerator

        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

        session_maker = async_sessionmaker(bind=conn, expire_on_commit=False)

        async def _get_session() -> AsyncGenerator[AsyncSession, None]:
            async with session_maker() as s:
                yield s

        app.dependency_overrides[get_session] = _get_session

        payload = {
            "username": "test2",
            "email": "t2@example.com",
            "password": "hunter2",
        }
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            r = await ac.post("/api/auth/register", json=payload)
            assert r.status_code == 200

            # Login expects form-encoded data and should succeed deterministically
            # because the test uses a single shared connection/sessionmaker.
            lr = await ac.post(
                "/api/auth/login",
                data={"username": "test2", "password": "hunter2"},
            )
            if lr.status_code != 200:
                raise AssertionError(
                    f"Login failed: status={lr.status_code}, body={lr.text}"
                )
            data = lr.json()
            assert "access_token" in data
            assert data.get("token_type") == "bearer"
    finally:
        # Ensure the connection is closed when the test completes
        await conn.close()
