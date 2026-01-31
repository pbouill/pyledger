from .base import TenantBase
from sqlalchemy import Integer, String, Float, Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

class InvoiceItem(TenantBase):
    __tablename__ = "invoice_item"
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoice.id"), nullable=False)
    value = Column(Float, nullable=False)
    tax_rate = Column(Float, nullable=True)
    description = Column(String, nullable=True)
    # created_at provided by TenantBase (timezone-aware)
    invoice = relationship("Invoice", back_populates="items")
