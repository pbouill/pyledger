from .base import TenantBase
from sqlalchemy import Integer, String, Column

class Project(TenantBase):
    __tablename__ = "project"
    id = Column(Integer, primary_key=True)
    # Add other fields as needed
