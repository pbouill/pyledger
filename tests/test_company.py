from httpx import ASGITransport, AsyncClient

from canon.app import create_app
from canon.db import get_session


async def test_list_currencies_and_create_company() -> None:
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    app = create_app(engine=engine)

    # Acquire a dedicated connection for this test and create tables there
    conn = await engine.connect()
    try:
        from canon.models import Base

        await conn.run_sync(Base.metadata.create_all)

        from typing import AsyncGenerator

        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

        session_maker = async_sessionmaker(bind=conn, expire_on_commit=False)

        async def _get_session() -> AsyncGenerator[AsyncSession, None]:
            async with session_maker() as s:
                yield s

        app.dependency_overrides[get_session] = _get_session

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # Register and login a user
            r = await ac.post(
                "/api/auth/register",
                json={
                    "username": "cmpuser",
                    "email": "cmp@example.com",
                    "password": "hunter2",
                },
            )
            assert r.status_code == 200
            lr = await ac.post(
                "/api/auth/login",
                data={"username": "cmpuser", "password": "hunter2"},
            )
            assert lr.status_code == 200
            token = lr.json().get("access_token")
            assert token

            # List currencies (new endpoint path returns mapping)
            cr = await ac.get("/api/currency/")
            assert cr.status_code == 200
            assert isinstance(cr.json(), dict)
            assert "USD" in cr.json().keys()

            # Create company using USD
            hr = await ac.post(
                "/api/company/",
                json={
                    "name": "TestCo",
                    "legal_name": "Test Company LLC",
                    "tax_number": "TN123",
                    "currency_code": "USD",
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            assert hr.status_code == 200
            data = hr.json()
            assert data.get("name") == "TestCo"
            assert data.get("currency_code") == "USD"
    finally:
        await conn.close()
