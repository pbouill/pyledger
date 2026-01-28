from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from canon.app import create_app
from canon.db import get_session


async def fake_session() -> AsyncGenerator[object, None]:
    class Dummy:
        async def execute(self, *args: object, **kwargs: object) -> None:
            return None

    yield Dummy()


@pytest.mark.asyncio
async def test_health() -> None:
    app = create_app()
    app.dependency_overrides[get_session] = fake_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/health")

    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
