from httpx import ASGITransport, AsyncClient

from canon.app import create_app
from canon.db import get_session


async def test_register_duplicate_returns_400_and_message() -> None:
    from typing import AsyncGenerator

    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    app = create_app(engine=engine)

    # Acquire a dedicated connection and setup session override
    conn = await engine.connect()
    try:
        from canon.models import Base

        await conn.run_sync(Base.metadata.create_all)

        session_maker = async_sessionmaker(bind=conn, expire_on_commit=False)

        async def _get_session() -> AsyncGenerator[AsyncSession, None]:
            async with session_maker() as s:
                yield s

        app.dependency_overrides[get_session] = _get_session

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            r = await ac.post(
                "/api/auth/register",
                json={
                    "username": "dupuser",
                    "email": "dup@example.com",
                    "password": "hunter2",
                },
            )
            assert r.status_code == 200
            r2 = await ac.post(
                "/api/auth/register",
                json={
                    "username": "dupuser",
                    "email": "dup@example.com",
                    "password": "hunter2",
                },
            )
            assert r2.status_code == 400
            assert r2.json().get("detail")
            assert r2.headers.get("X-App-Message") is not None
            assert "already" in r2.headers.get("X-App-Message", "").lower()
    finally:
        await conn.close()