"""SQLAlchemy model base and placeholder models for PyLedger.

Keep models minimal to start; add more domain models as needed.
"""
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Company(Base):
    __tablename__ = "company"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Add additional domain models here (Account, Transaction, User, etc.)
