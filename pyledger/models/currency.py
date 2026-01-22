from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import Session as SASession

from .base import Base
from .currency_rate import CurrencyRate


class Currency(Base):
    __tablename__ = "currency"
    code: Mapped[str] = mapped_column(
        String(8), primary_key=True
    )  # e.g. 'USD', 'EUR'
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    symbol: Mapped[str | None] = mapped_column(String(8), nullable=True)
    rates: Mapped[list["CurrencyRate"]] = relationship(
        "CurrencyRate",
        back_populates="currency",
    )

    def get_rate(
        self, session: "SASession", at: datetime | None = None
    ) -> float | None:
        """
        Return the rate_vs_usd for this currency at a specific datetime, or the
        latest if not provided.
        """
        q = session.query(CurrencyRate).filter_by(currency_code=self.code)
        if at:
            q = q.filter(CurrencyRate.timestamp <= at)
        q = q.order_by(CurrencyRate.timestamp.desc())
        rate = q.first()
        return rate.rate_vs_usd if rate else None

    @classmethod
    async def update_all_rates(cls, session: "SASession") -> None:
        """
        Update all currency rates in the table using the external API and store
        them in currency_rate.
        """
        rates = []
        async for rate in await CurrencyRate.RATE_PROVIDER.iter_rates():
            rates.append(rate)
        session.add_all(rates)
        await session.commit()  # type: ignore[func-returns-value]
