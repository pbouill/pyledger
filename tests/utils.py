from httpx import AsyncClient


async def get_token(
    ac: AsyncClient, username: str, email: str, password: str = "hunter2"
) -> str:
    """Register and login a user using the provided AsyncClient and return a token."""
    r = await ac.post(
        "/api/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    r.raise_for_status()
    lr = await ac.post(
        "/api/auth/login",
        data={"username": username, "password": password},
    )
    lr.raise_for_status()
    return lr.json().get("access_token")
