from .base import TenantBase
from sqlalchemy import Integer, String, Float, Column, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone

class EntryType(enum.Enum):
    expense = "expense"
    income = "income"
    invoice = "invoice"
    remittance = "remittance"

class Ledger(TenantBase):
    __tablename__ = "ledger"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("account.id"), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    description = Column(String, nullable=True)
    related_expense_id = Column(Integer, ForeignKey("expense.id"), nullable=True)
    related_income_id = Column(Integer, nullable=True)  # Placeholder for future
    related_invoice_id = Column(Integer, ForeignKey("invoice.id"), nullable=True)
    entry_type = Column(Enum(EntryType), nullable=False)
    # created_at provided by TenantBase (timezone-aware)
