import copy
import json
import os
from typing import AsyncGenerator, Optional

import httpx
import pytest

from canon.models.currency_rate import ERAPI, CurrencyRate


@pytest.fixture(scope="session")
def erapi_fixture() -> dict:
    fixture_path = os.path.join(
        os.path.dirname(__file__),
        "resources",
        "erapi_fixture.json",
    )
    if not os.path.exists(fixture_path):
        # Only fetch and save if not present
        url = ERAPI.CURRENCY_EXCHANGE_API_URL.format(base="USD")
        resp = httpx.get(url)
        resp.raise_for_status()
        raw_data = resp.json()
        os.makedirs(os.path.dirname(fixture_path), exist_ok=True)
        with open(fixture_path, "w") as f:
            json.dump(raw_data, f, indent=2)
    with open(fixture_path) as f:
        return json.load(f)


@pytest.mark.asyncio
async def test_erapi_iter_rates_with_fixture(erapi_fixture: dict) -> None:
    # Patch ERAPI.make_request to use the fixture
    class MockERAPI(ERAPI):
        @classmethod
        async def make_request(cls, base: str = "USD") -> "ERAPI":
            # Use the fixture only if base is USD, else fallback to real request
            if base == "USD":
                return cls.model_validate(erapi_fixture)
            else:
                base_rate: Optional[float] = erapi_fixture["rates"].get(base)
                if not base_rate:
                    raise ValueError(f"Fixture does not contain rate for base: {base}")
                # Adjust rates to simulate different base
                adjusted_fixture = copy.deepcopy(erapi_fixture)
                adjusted_fixture["base_code"] = base
                async for code, rate in adjusted_fixture["rates"].items():
                    # Ensure division and float conversion
                    adjusted_fixture["rates"][code] = float(rate) / float(base_rate)
                adjusted_fixture["rates"][base] = 1.0
                return cls.model_validate(adjusted_fixture)

    # Patch iter_rates to use MockERAPI.make_request
    async def mock_iter_rates(base: str = "USD") -> AsyncGenerator[CurrencyRate, None]:
        erapi = await MockERAPI.make_request(base)
        async for rate in erapi.iter_rates():
            yield rate

    rates = []
    async for rate in mock_iter_rates(base="USD"):
        assert hasattr(rate, "currency_code")
        assert hasattr(rate, "rate_vs_usd")
        assert hasattr(rate, "timestamp")
        assert isinstance(rate.currency_code, str)
        assert isinstance(rate.rate_vs_usd, float)
        assert rate.rate_vs_usd > 0
        rates.append(rate)
    assert len(rates) > 10
