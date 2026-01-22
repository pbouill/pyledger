from sqlalchemy import Column, String

from .base import Base


class Country(Base):
    __tablename__ = "country"
    code = Column(String(2), primary_key=True)  # ISO 3166-1 alpha-2
    name = Column(String(128), nullable=False)
    default_currency = Column(String(8), nullable=True)
    default_language = Column(String(16), nullable=True)
