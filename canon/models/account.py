from typing import Optional

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from canon.enums.account import AccountType

from .base import Base


class Account(Base):
    __tablename__ = "account"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    institution: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    currency_code: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    account_type: Mapped[AccountType] = mapped_column(
        SAEnum(AccountType, name="account_type"), nullable=False
    )
    opening_balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Relationship to transactions in the same DB
    transactions = relationship("AccountTransaction", back_populates="account")
