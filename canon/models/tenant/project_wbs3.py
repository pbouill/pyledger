from .base import TenantBase
from sqlalchemy import Integer, String, Column, ForeignKey, Text

class ProjectWBS3(TenantBase):
    __tablename__ = "project_wbs3"
    id = Column(Integer, primary_key=True)
    wbs2_id = Column(Integer, ForeignKey("project_wbs2.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
