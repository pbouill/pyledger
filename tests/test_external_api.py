import pytest

from pyledger.models.currency_rate import ERAPI


@pytest.mark.asyncio
async def test_currency_rate_api() -> None:
    """
    The API returns rates for all supported codes vs USD in one response.
    This test checks several common codes to ensure integration works.
    """
    codes = ["EUR", "GBP", "JPY", "CAD", "AUD", "USD"]
    resp = await ERAPI.make_request()
    for code in codes:
        rate = resp.rates.get(code)
        assert isinstance(
            rate, (float, int)
        ), f"Rate for {code} should be a number, got {rate}"
        assert rate and rate > 0, (
            f"Rate for {code} should be positive, got {rate}"
        )
