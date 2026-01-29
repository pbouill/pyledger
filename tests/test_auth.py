from httpx import ASGITransport, AsyncClient

import canon.api.auth as auth_mod
from canon.app import create_app


async def test_login_with_form_fails_with_no_user() -> None:
    async def fake_get_user(db: object, username: str) -> None:
        return None

    original_get_user = auth_mod.get_user_by_username
    try:
        auth_mod.get_user_by_username = fake_get_user

        app = create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            r = await ac.post(
                "/api/auth/login",
                data={"username": "noone", "password": "pw"},
            )
        assert r.status_code == 401
    finally:
        auth_mod.get_user_by_username = original_get_user
