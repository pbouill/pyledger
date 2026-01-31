from .base import TenantBase
from sqlalchemy import Integer, String, Column

class Payroll(TenantBase):
    __tablename__ = "payroll"
    id = Column(Integer, primary_key=True)
    # Add other fields as needed
