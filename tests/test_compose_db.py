
from typing import Any

import pytest
from sqlalchemy import Inspector, inspect, text
from sqlalchemy.ext.asyncio import AsyncEngine

from canon.models.base import TableNames


@pytest.mark.integration
async def test_db_tables_exist(engine: AsyncEngine) -> None:
    async with engine.connect() as conn:
        def get_tables(sync_conn: Any) -> Any:
            inspector: Inspector = inspect(sync_conn)
            return inspector.get_table_names()
        actual_tables = await conn.run_sync(get_tables)
        for table in TableNames:
            assert table in actual_tables, f"Missing table: {table}"

@pytest.mark.compose
async def test_db_insert_and_select(engine: AsyncEngine) -> None:
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1
