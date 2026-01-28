"""
Custom SQLAlchemy column type for serializing/deserializing CompanySettingsSchema
(Pydantic) objects to/from JSON.
"""
from typing import Optional

import pycountry
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from .base import PydanticTypeDecorator
from .currency import Currency


class CompanySettingsSchema(BaseModel):
    """
    Pydantic schema for company settings, with ISO code validation for language
    and currency.
    """
    invoice_prefix: Optional[str] = None
    default_language_code: Optional[str] = None  # ISO 639-1 or -3
    default_currency_code: Optional[str] = None  # ISO 4217
    timezone: Optional[str] = None  # Store as IANA tz string
    # Add more settings fields as needed

    @field_validator("default_language_code")
    @classmethod
    def validate_language_code(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            pycountry.languages.lookup(v)
        except Exception as err:
            raise ValueError(f"Invalid language code: {v}") from err
        return v

    @field_validator("default_currency_code")
    @classmethod
    def validate_currency_code(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            pycountry.currencies.lookup(v)
        except Exception as err:
            raise ValueError(f"Invalid currency code: {v}") from err
        return v


    def get_default_currency(self, session: Session) -> Currency | None:
        """
        Return the Currency SQLAlchemy object for the default_currency code, or
        None if not found.
        """
        if not self.default_currency_code:
            return None
        return (
            session.query(Currency)
            .filter_by(code=self.default_currency_code)
            .one_or_none()
        )

class CompanySettingsType(PydanticTypeDecorator[CompanySettingsSchema]):
    """Stores CompanySettingsSchema as JSON in the database."""
    pass