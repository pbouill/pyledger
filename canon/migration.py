import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine

from .db import get_engine
from .models import Base

logger = logging.getLogger(__name__)

async def migrate_database(engine: Optional[AsyncEngine] = None) -> AsyncEngine:
    """Perform database migrations using SQLAlchemy's metadata.

    After creating shared tables, ensure any already-registered companies have
    their per-company tenant databases created and initialized.
    """
    engine = engine or get_engine()
    logger.info("Starting database migration...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Perform tenant DB provisioning for existing companies. This is a best-effort
    # step: failures here should not prevent the main migration from completing.
    try:
        from sqlalchemy import select
        from sqlalchemy.ext.asyncio import async_sessionmaker

        from canon.models.company import Company
        from canon.util.tenant import create_company_database

        session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
        async with session_maker() as session:
            res = await session.execute(select(Company.id))
            ids = [row[0] for row in res.fetchall()]
            for cid in ids:
                try:
                    await create_company_database(cid)
                    logger.info("Ensured tenant DB for company %s", cid)
                except Exception:  # pragma: no cover - operational
                    logger.exception("Failed to create tenant DB for company %s", cid)

        # After provisioning tenant DBs, run tenant-level migrations/consistency checks.
        # These scripts are best-effort and will log failures without failing startup.
        try:
            # Import local scripts that operate across tenant DBs (they scan .local/)
            from scripts.migrate_tenant_add_timestamps import main as _migrate_timestamps
            from scripts.migrate_add_payroll_spec_columns import main as _migrate_payroll_cols
            from scripts.migrate_add_payroll_spec_unique import main as _migrate_payroll_unique
            from scripts.migrate_create_categories_table import main as _migrate_categories
            from scripts.migrate_add_category_code import main as _migrate_category_code
            from scripts.migrate_drop_payroll_spec_name import main as _migrate_drop_name

            logger.info("Running tenant-level migrations: timestamps, payroll spec columns, unique idx, categories, category codes, dropping deprecated columns")
            _migrate_timestamps()
            _migrate_payroll_cols()
            _migrate_payroll_unique()
            _migrate_categories()
            _migrate_category_code()
            _migrate_drop_name()
            logger.info("Tenant-level migrations completed")
        except Exception:  # pragma: no cover - operational
            logger.exception("Failed running tenant-level migrations")

    except Exception:  # pragma: no cover - defensive
        logger.exception("Error while provisioning tenant DBs")

    logger.info("Database migration completed.")
    return engine
