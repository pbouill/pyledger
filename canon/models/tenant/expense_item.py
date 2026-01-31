from .base import TenantBase
from sqlalchemy import Integer, String, Float, Column, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

class ExpenseItem(TenantBase):
    __tablename__ = "expense_item"
    id = Column(Integer, primary_key=True)
    expense_id = Column(Integer, ForeignKey("expense.id"), nullable=False)
    value = Column(Float, nullable=False)
    tax_rate = Column(Float, nullable=True)
    expense_category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    description = Column(String, nullable=True)
    is_remittance = Column(Boolean, default=False)
    due_date = Column(DateTime, nullable=True)
    # created_at provided by TenantBase (timezone-aware)
    expense = relationship("Expense", back_populates="items")
