








import pycountry
from pydantic import field_validator

from canon.models.base import PydanticBase

from .base import PydanticTypeDecorator


class AddressSchema(PydanticBase):
    """
    Pydantic schema for postal addresses, with ISO code validation for country,
    language, and currency.
    """
    street: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country_code: str | None = None  # ISO 3166-1 alpha-2


    @field_validator("country_code")
    @classmethod
    def validate_country_code(cls, v: str | None) -> str | None:
        """Validate that the country code is a valid ISO 3166-1 code."""
        if v is None:
            return v
        try:
            pycountry.countries.lookup(v)
        except Exception as err:
            raise ValueError(f"Invalid country code: {v}") from err
        return v


class AddressType(PydanticTypeDecorator[AddressSchema]):
    """Stores AddressSchema as JSON in the database."""
    pass
