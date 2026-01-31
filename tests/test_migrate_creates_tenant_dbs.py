from unittest.mock import AsyncMock, patch

from sqlalchemy.ext.asyncio import create_async_engine

from canon.migration import migrate_database
from canon.models import Base
from canon.models.company import Company


async def test_migrate_provisions_tenant_db() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    conn = await engine.connect()
    try:
        # Create tables and insert a company row
        await conn.run_sync(Base.metadata.create_all)
        from sqlalchemy import insert

        await conn.execute(
            insert(Company).values(name="Pre", legal_name="Pre Co")
        )
        await conn.commit()

        with patch(
            "canon.util.tenant.create_company_database", new=AsyncMock()
        ) as mock_create:
            await migrate_database(engine)
            assert mock_create.await_count == 1
    finally:
        await conn.close()
