import os
os.environ["DB_HOST"] = "localhost"
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import create_engine, inspect
import pytest
from pyledger.config import get_database_url

load_dotenv()

DB_URL = get_database_url()

@pytest.mark.integration
def test_db_tables_exist():
    assert DB_URL, "Database URL could not be constructed from config."
    engine = create_engine(DB_URL)
    inspector = inspect(engine)
    expected_tables = [
        "company", "user", "currency", "currency_rate"
    ]
    actual_tables = inspector.get_table_names()
    for table in expected_tables:
        assert table in actual_tables, f"Missing table: {table}"

@pytest.mark.compose
def test_db_insert_and_select():
    assert DB_URL, "Database URL could not be constructed from config."
    engine = sa.create_engine(DB_URL)
    with engine.connect() as conn:
        result = conn.execute(sa.text("SELECT 1")).scalar()
        assert result == 1
