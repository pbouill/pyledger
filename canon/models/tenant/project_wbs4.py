from .base import TenantBase
from sqlalchemy import Integer, String, Column, ForeignKey, Text, Float, Date

class ProjectWBS4(TenantBase):
    __tablename__ = "project_wbs4"
    id = Column(Integer, primary_key=True)
    wbs3_id = Column(Integer, ForeignKey("project_wbs3.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    budget_hours = Column(Float, nullable=True)
    budget_cost = Column(Float, nullable=True)
    start_date = Column(Date, nullable=True)
    completion_date = Column(Date, nullable=True)
