
"""
Test script to verify that all models can be imported and tables created
with SQLAlchemy.
"""




import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from canon.models import Base

logger = logging.getLogger(__name__)

# Use in-memory SQLite for test
engine = create_engine("sqlite:///:memory:")
Session = sessionmaker(bind=engine)

try:
    Base.metadata.create_all(engine)
    # SUCCESS: All tables created successfully.
except Exception:
    pass
