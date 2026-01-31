from enum import StrEnum
from .base import TenantBase
from sqlalchemy import Integer, String, Column, Text, Enum, Date, UniqueConstraint


class PeriodMode(StrEnum):
    ANNUALIZED = "annualized"
    CUMULATIVE = "cumulative"


class PayrollSpec(TenantBase):
    __tablename__ = "payroll_spec"
    __table_args__ = (
        # enforce uniqueness: (jurisdiction, active_date) must be unique to avoid
        # overlapping specs for the same jurisdiction on the same active date
        UniqueConstraint("jurisdiction", "active_date", name="uq_payroll_spec_jur_active"),
    )

    id = Column(Integer, primary_key=True)
    # canonical code like 'CA-ON-2026' (machine identifier)
    code = Column(String, nullable=False)
    currency = Column(String, nullable=True)
    period_mode = Column(Enum(PeriodMode), nullable=True)
    active_date = Column(Date, nullable=True)
    # optional human-readable comment or description sourced from meta.comment
    comment = Column(Text, nullable=True)
    # legacy columns retained for compatibility (we're deprecating `name` usage)
    year = Column(Integer, nullable=False)
    jurisdiction = Column(String, nullable=False)
    spec_yaml = Column(Text, nullable=False)
