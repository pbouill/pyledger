"""
Test script to verify that all models can be imported and tables created with SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from canonledger.models import Base

# Use in-memory SQLite for test
engine = create_engine("sqlite:///:memory:")
Session = sessionmaker(bind=engine)

try:
    Base.metadata.create_all(engine)
    print("SUCCESS: All tables created successfully.")
except Exception as e:
    print(f"ERROR: Table creation failed: {e}")
