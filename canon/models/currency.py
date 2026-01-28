
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import Session as SASession

from .base import Base, TableNames
from .relationships import build_single_relationship, get_parent_relationship_def

if TYPE_CHECKING:
    from .currency_rate import CurrencyRate

RATES_RELATIONSHIP_DEF = TableNames.CURRENCY_RATE, get_parent_relationship_def(
    TableNames.CURRENCY, TableNames.CURRENCY_RATE
    )


class Currency(Base):
    __tablename__ = TableNames.CURRENCY
    # __allow_unmapped__ = True
    code: Mapped[str] = mapped_column(String(8), primary_key=True)  # e.g. 'USD', 'EUR'
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    symbol: Mapped[str | None] = mapped_column(String(8), nullable=True)
    rates: Mapped[list["CurrencyRate"]] = build_single_relationship(
        *RATES_RELATIONSHIP_DEF
    )
    # rates: Mapped[list[CurrencyRate]] = relationship(
    #     back_populates=__tablename__
    # )
    # if TYPE_CHECKING:
    # rates: Mapped[list['CurrencyRate']] = Column('rates')
    # # For type checkers (populated by SQLAlchemy at runtime)
    # if TYPE_CHECKING:
    #     rates: list[CurrencyRate]  # back-propagated by CurrencyRate.currency

    def get_rate(
        self, session: SASession, at: Optional[datetime] = None
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

