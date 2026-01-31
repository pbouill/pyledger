from .base import TenantBase
from sqlalchemy import Integer, String, Column, DateTime, ForeignKey, LargeBinary
from datetime import datetime

class EmployeeItem(TenantBase):
    __tablename__ = "employee_item"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employee.id"), nullable=False)
    filename = Column(String, nullable=False)
    category = Column(String, nullable=True)
    date = Column(DateTime, nullable=True)
    blob = Column(LargeBinary, nullable=True)
    notes = Column(String, nullable=True)
