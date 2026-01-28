import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import AsyncGenerator, ClassVar, Optional, Self

import httpx
import pycountry
from pydantic import BaseModel, field_validator
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from .base import Base, TableNames
from .currency import Currency, RATES_RELATIONSHIP_DEF
# from .relationships import RELATIONSHIPS

logger = logging.getLogger(__name__)

RATE_BASE: str = "USD"

class CurrencyRateProvider(ABC):
    """
    Abstract base class for currency rate providers.
    """

    @classmethod
    @abstractmethod
    async def iter_rates(cls) -> AsyncGenerator["CurrencyRate", None]:
        """
        Asynchronously yield CurrencyRate objects.
        """
        raise NotImplementedError("Subclasses must implement iter_rates.")


# Pydantic model for open.er-api.com response
class ERAPI(BaseModel, CurrencyRateProvider):
    CURRENCY_EXCHANGE_API_URL: ClassVar[str] = "https://open.er-api.com/v6/latest/{base}"
    SUCCESS_CODE: ClassVar[str] = "success"
    
    result: str
    time_last_update_unix: Optional[datetime] = None
    time_last_update_utc: Optional[str] = None
    time_next_update_unix: Optional[datetime] = None
    time_next_update_utc: Optional[str] = None
    time_eol_unix: Optional[datetime] = None
    base_code: str
    rates: dict[str, float]


    @field_validator(
        "time_last_update_unix",
        "time_next_update_unix",
        "time_eol_unix",
        mode="before",
    )
    @classmethod
    def validate_unix_fields(cls, v: int) -> None | datetime:
        if not isinstance(v, int):
            raise ValueError("Invalid unix timestamp")
        if v == 0:
            return None
        return datetime.fromtimestamp(v)

    @field_validator("base_code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        try:
            pycountry.currencies.lookup(v)
        except LookupError as err:
            raise ValueError(f"Invalid currency code: {v}") from err
        return v

    @classmethod
    async def make_request(cls, base: str = RATE_BASE) -> "ERAPI":
        url = cls.CURRENCY_EXCHANGE_API_URL.format(base=base)
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            obj = cls.model_validate(data)
            if obj.result != cls.SUCCESS_CODE:
                raise ValueError(
                    f"API returned error result: {obj.result}. {obj}"
                )
            if obj.base_code != base:
                raise ValueError(
                    f"API returned unexpected base code: {obj.base_code}, "
                    f"expected {base}"
                )
            return obj
    
    @classmethod
    async def iter_rates(cls) -> AsyncGenerator["CurrencyRate", None]:  # type: ignore[override]
        erapi = await cls.make_request()
        if not isinstance(erapi.time_last_update_unix, datetime):
            raise ValueError(
                f"Invalid time_last_update_unix value: {erapi.time_last_update_unix} "
                f"({type(erapi.time_last_update_unix)})"
            )
        if not erapi.base_code == RATE_BASE:
            raise ValueError(
                f"API returned unexpected base code: {erapi.base_code}, "
                f"expected {RATE_BASE}"
            )
        for code, rate in erapi.rates.items():
            logger.debug(f"Checking currency code: {repr(code)}")
            try:
                code = cls.validate_code(code)
            except ValueError as err:
                logger.warning(
                    f"Skipping invalid currency code: {repr(code)}. "
                    f"Reason: {err}"
                )
                continue
            obj = CurrencyRate()
            obj.currency_code = code
            obj.rate_vs_usd = rate
            obj.timestamp = erapi.time_last_update_unix
            yield obj
    

class CurrencyRate(Base):
    __tablename__ = TableNames.CURRENCY_RATE
    __table_args__ = {'extend_existing': True}

    RATE_PROVIDER: type[CurrencyRateProvider] = ERAPI

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    currency_code: Mapped[str] = mapped_column(
        String(8), ForeignKey(Currency.code), nullable=False
    )
    currency: Mapped[Currency] = relationship(
        Currency,
        back_populates=RATES_RELATIONSHIP_DEF[1].parent_attr,
    )
    rate_vs_usd: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    @classmethod
    async def update_all(cls, session: Session) -> list[Self]:
        """
        Update all currency rates in the table using the external API and store
        them in currency_rate.
        """
        rates: list[Self] = []
        rates_gen = await cls.RATE_PROVIDER.iter_rates()
        async for rate in rates_gen:
            rates.append(rate)  # type: ignore[arg-type]
        session.add_all(rates)
        await session.commit()  # type: ignore[func-returns-value]
        logger.info(f"Currency rates updated successfully ({len(rates)} rates).")
        return rates
