from httpx import AsyncClient


async def test_duplicate_legal_name_and_tax_number_return_400(
    async_client: AsyncClient, token: str
) -> None:
    ac = async_client

    # Create first company
    hr = await ac.post(
        "/api/company/",
        json={
            "name": "UniqueCo",
            "legal_name": "Unique Company LLC",
            "tax_number": "TAX123",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert hr.status_code == 200

    # Duplicate legal_name
    hr2 = await ac.post(
        "/api/company/",
        json={
            "name": "OtherCo",
            "legal_name": "Unique Company LLC",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert hr2.status_code == 400
    assert hr2.json().get("detail")
    assert hr2.headers.get("X-App-Message") is not None
    assert "legal" in hr2.json().get("detail", "").lower()

    # Duplicate tax_number
    hr3 = await ac.post(
        "/api/company/",
        json={
            "name": "OtherCo2",
            "tax_number": "TAX123",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert hr3.status_code == 400
    assert hr3.json().get("detail")
    assert hr3.headers.get("X-App-Message") is not None
    assert "tax" in hr3.json().get("detail", "").lower()
