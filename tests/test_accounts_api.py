from httpx import AsyncClient


async def test_accounts_crud(async_client: AsyncClient, token: str) -> None:
    ac = async_client

    # Create company
    r = await ac.post(
        "/api/company/",
        json={"name": "AcctCo", "legal_name": "Acct Company"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    company = r.json()
    cid = company.get("id")
    assert cid

    # Create account
    payload = {
        "name": "Primary Checking",
        "institution": "Bank X",
        "currency_code": "USD",
        "account_type": "chequing",
    }
    r2 = await ac.post(
        f"/api/company/{cid}/accounts/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r2.status_code == 200
    acct = r2.json()
    assert acct.get("id")
    aid = acct.get("id")

    # List accounts
    r3 = await ac.get(
        f"/api/company/{cid}/accounts/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r3.status_code == 200
    assert any(a.get("id") == aid for a in r3.json())

    # Create transaction
    tx_payload = {"amount": 100.0, "currency_code": "USD", "description": "Deposit"}
    r4 = await ac.post(
        f"/api/company/{cid}/accounts/{aid}/transactions",
        json=tx_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r4.status_code == 200
    tx = r4.json()
    assert tx.get("id")

    # List transactions
    r5 = await ac.get(
        f"/api/company/{cid}/accounts/{aid}/transactions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r5.status_code == 200
    assert any(t.get("id") == tx.get("id") for t in r5.json())
