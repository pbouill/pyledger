from .base import TenantBase
from sqlalchemy import Integer, String, Column, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship


class Category(TenantBase):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    # Optional machine-friendly code for deterministic upserts and parent refs
    code = Column(String, nullable=True, unique=False)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    parent = relationship("Category", remote_side=[id], backref="children")
    is_expense = Column(Boolean, default=True)
    is_income = Column(Boolean, default=False)
    comment = Column(Text, nullable=True)
