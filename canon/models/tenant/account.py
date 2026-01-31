
# Migrated from canon/models/account.py, now using TenantBase
from .base import TenantBase
from sqlalchemy import Integer, String, Float, Column

class Account(TenantBase):
    __tablename__ = "account"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    institution = Column(String, nullable=True)
    currency_code = Column(String, nullable=True)
    account_type = Column(String, nullable=False)
    opening_balance = Column(Float, nullable=True, default=0.0)
    # Add other fields as needed
