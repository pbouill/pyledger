from .base import TenantBase
from sqlalchemy import Integer, String, Column, ForeignKey, Text

class ProjectWBS2(TenantBase):
    __tablename__ = "project_wbs2"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
