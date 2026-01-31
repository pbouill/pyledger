from unittest.mock import AsyncMock, patch

from httpx import AsyncClient


async def test_create_company_triggers_tenant_db(
    async_client: AsyncClient, token: str
) -> None:
    # Patch the tenant creation helper so we don't actually attempt DB creates
    with patch(
        "canon.util.tenant.create_company_database",
        new=AsyncMock(return_value="base_company_1"),
    ) as mock_create:
        ac = async_client
        r = await ac.post(
            "/api/company/",
            json={"name": "CoForTenant", "legal_name": "CoTenant Ltd"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200
        # Ensure helper was called once with the created company id
        assert mock_create.await_count == 1
