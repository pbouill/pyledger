from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base


class AccountTransaction(Base):
    __tablename__ = "account_transaction"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("account.id"), nullable=False
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency_code: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    occurred_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    account = relationship("Account", back_populates="transactions")
