from .base import TenantBase
from sqlalchemy import Integer, String, Column, Float

class Rate(TenantBase):
    __tablename__ = "rate"
    id = Column(Integer, primary_key=True)
    # Add other fields as needed
