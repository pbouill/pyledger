import pytest
from pycountry import currencies


def validate_currency_code(code: str) -> str:
    try:
        currencies.lookup(code)
    except LookupError as err:
        raise ValueError(f"Invalid currency code: {code}") from err
    return code

@pytest.mark.parametrize("code", ["USD", "CAD", "EUR", "usd", "eur"])
def test_currency_code_validation(code: str) -> None:
    assert validate_currency_code(code) == code

@pytest.mark.parametrize("code", ["FAKE", "123", "", None])
def test_invalid_currency_code(code: str | None) -> None:
        with pytest.raises(ValueError):
            validate_currency_code(code)  # type: ignore[arg-type]
