from httpx import AsyncClient


async def test_list_currencies_and_create_company(
    async_client: AsyncClient, token: str
) -> None:
    ac = async_client

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