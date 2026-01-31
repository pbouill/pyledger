import logging
from types import SimpleNamespace

import pycountry
import pytest
from httpx import ASGITransport, AsyncClient

from canon.app import create_app


async def test_currency_endpoint_includes_usd() -> None:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/currency/")
        r2 = await ac.get("/api/currency")
    assert r.status_code == 200
    assert r2.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "USD" in data


async def test_currency_endpoint_logs_on_bad_entries(
    monkeypatch: "pytest.MonkeyPatch", caplog: "pytest.LogCaptureFixture"
) -> None:
    # Replace pycountry.currencies with a list that contains bad entries
    fake = [
        SimpleNamespace(alpha_3=None, name="NoCode"),
        SimpleNamespace(alpha_3="NONAME", name=None),
        SimpleNamespace(alpha_3="USD", name="United States dollar"),
        SimpleNamespace(alpha_3="USD", name="Duplicate USD"),
    ]
    monkeypatch.setattr(pycountry, "currencies", fake)

    app = create_app()
    transport = ASGITransport(app=app)
    caplog.set_level(logging.WARNING)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/currency/")
    assert r.status_code == 200
    data = r.json()
    # USD should be present once with the first valid name
    assert data.get("USD") == "United States dollar"
    # Warnings should have been emitted for missing fields and duplicates
    messages = [rec.message.lower() for rec in caplog.records]
    assert any("missing fields" in m for m in messages)
    assert any("duplicate currency code" in m for m in messages)
