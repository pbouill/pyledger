from .base import TenantBase
from sqlalchemy import Integer, String, Float, Column, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

class Invoice(TenantBase):
    __tablename__ = "invoice"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=True)
    employee_id = Column(Integer, ForeignKey("employee.id"), nullable=True)
    due_date = Column(DateTime, nullable=True)
    issued_date = Column(DateTime, nullable=True)
    status = Column(String, nullable=True)
    total = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    # timestamps provided by TenantBase (timezone-aware)
    items = relationship("InvoiceItem", back_populates="invoice")
