from .base import TenantBase
from sqlalchemy import Integer, String, Column, DateTime, Boolean, JSON
from datetime import datetime

class Employee(TenantBase):
    """Tenant `Employee` model.

    Added `payroll_tax_deductions` as a JSON column to store per-employee
    payroll-related TD1 values and other deduction metadata. Example shape:

    {
        "td1_fed": {"basic_personal_amount": 15000, "additional_amount": 0},
        "td1_prov": {"basic_personal_amount": 11865},
        "other": {"dependents": 2}
    }
    """

    __tablename__ = "employee"
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    SIN = Column(String, nullable=True)
    # Store TD1 and other payroll-specific per-employee deductions/tax overrides
    payroll_tax_deductions = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)