"""SQLAlchemy model base and placeholder models for PyLedger.

Keep models minimal to start; add more domain models as needed.
"""
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Company(Base):
    __tablename__ = "company"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Add additional domain models here (Account, Transaction, User, etc.)
