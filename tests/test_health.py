import pytest
from httpx import AsyncClient, ASGITransport

from pyledger.app import create_app
from pyledger.db import get_session


async def fake_session():
    class Dummy:
        async def execute(self, *args, **kwargs):
            return None

    yield Dummy()


@pytest.mark.asyncio
async def test_health():
    app = create_app()
    app.dependency_overrides[get_session] = fake_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/health")

    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
