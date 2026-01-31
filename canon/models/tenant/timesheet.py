from .base import TenantBase
from sqlalchemy import Integer, Float, Column, ForeignKey, Date, Text, DateTime
from datetime import datetime

class Timesheet(TenantBase):
    __tablename__ = "timesheet"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employee.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    wbs4_id = Column(Integer, ForeignKey("project_wbs4.id"), nullable=True)
    date = Column(Date, nullable=False)
    hours = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    # created_at provided by TenantBase (timezone-aware)
