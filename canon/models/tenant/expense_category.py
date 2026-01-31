from .base import TenantBase
from sqlalchemy import Integer, String, Column, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship


# Deprecated: keep this model for backwards compatibility but map to the
# new `categories` table. Prefer using `Category` from `category.py`.
class ExpenseCategory(TenantBase):
    __tablename__ = "categories"  # intentionally point to new table
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    is_expense = Column(Boolean, default=True)
    is_income = Column(Boolean, default=False)
    comment = Column(Text, nullable=True)
    parent = relationship("ExpenseCategory", remote_side=[id], backref="children")
