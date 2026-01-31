import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from canon.config import get_database_url
from canon.models import Base
from canon.models.tenant import TenantBase

logger = logging.getLogger(__name__)


async def create_company_database(company_id: int) -> str:
    """Create a dedicated database for a company and run migrations.

    Database will be named like: {base_db_name}_company_{id}

    Returns the created DB name.
    """
    # Parse base DB url and build admin and tenant URLs.
    DATABASE_URL = get_database_url()
    if DATABASE_URL.startswith("postgresql://"):
        # Postgres multi-tenant DB creation logic (if needed, keep using Base)
        async_database_url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        base_db_name = DATABASE_URL.rsplit("/", 1)[-1]
        tenant_db_name = f"{base_db_name}_company_{company_id}"
        admin_url = async_database_url.rsplit("/", 1)[0] + "/postgres"
        admin_engine: AsyncEngine = create_async_engine(admin_url)
        try:
            async with admin_engine.begin() as conn:
                # Check if DB exists
                res = await conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :name"),
                    {"name": tenant_db_name},
                )
                if res.scalar_one_or_none() is None:
                    logger.info("Creating tenant DB %s", tenant_db_name)
                    await conn.execute(text(f'CREATE DATABASE "{tenant_db_name}"'))
                else:
                    logger.info("Tenant DB %s already exists", tenant_db_name)
        finally:
            await admin_engine.dispose()

        # Run migrations (create tables) on the new DB
        tenant_url = async_database_url.rsplit("/", 1)[0] + f"/{tenant_db_name}"
        tenant_engine_pg: AsyncEngine = create_async_engine(tenant_url)
        try:
            async with tenant_engine_pg.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        finally:
            await tenant_engine_pg.dispose()

        # Optional: auto-seed default payroll spec for new tenants if configured
        from os import getenv

        default_spec = getenv("DEFAULT_PAYROLL_SPEC_YML")
        if default_spec:
            try:
                # Import seeder dynamically to avoid startup overhead
                from scripts.seed_payroll_spec import seed_payroll_spec

                # Run seeder asynchronously for this new company
                import asyncio

                asyncio.create_task(seed_payroll_spec(company_id, default_spec))
            except Exception:  # pragma: no cover - operational
                logger.exception("Failed to seed default payroll spec for %s", company_id)
        else:
            # Auto-seed all YAML files in seed/payroll/ except template.yml
            try:
                from scripts.seed_payroll_spec import seed_payroll_spec
                from pathlib import Path
                import asyncio

                seed_dir = Path("seed/payroll")
                if seed_dir.exists():
                    for yml in sorted(seed_dir.glob("*.yml")):
                        if yml.name.lower() == "template.yml":
                            continue
                        try:
                            asyncio.create_task(seed_payroll_spec(company_id, str(yml)))
                        except Exception:  # pragma: no cover - operational
                            logger.exception("Failed to seed payroll spec %s for company %s", yml, company_id)
            except Exception:  # pragma: no cover - operational
                logger.exception("Failed scanning seed/payroll for specs for %s", company_id)

            # Auto-seed categories too
            try:
                from scripts.seed_categories import seed_categories
                from pathlib import Path
                import asyncio

                cat_dir = Path("seed/categories")
                if cat_dir.exists():
                    for yml in sorted(cat_dir.glob("*.yml")):
                        if yml.name.lower() == "template.yml":
                            continue
                        try:
                            asyncio.create_task(seed_categories(company_id, str(yml)))
                        except Exception:  # pragma: no cover - operational
                            logger.exception("Failed to seed categories %s for company %s", yml, company_id)
            except Exception:  # pragma: no cover - operational
                logger.exception("Failed scanning seed/categories for specs for %s", company_id)
        return tenant_db_name

    elif DATABASE_URL.startswith("sqlite+aiosqlite:///"):
        # SQLite multi-tenant DB creation logic
        # Main DB is .local/app.db, tenant DBs are .local/company_{id}.db
        import os
        db_dir = os.getenv("DB_PATH", ".local/")
        if not db_dir.endswith("/"):
            db_dir += "/"
        tenant_db_file = f"{db_dir}company_{company_id}.db"
        tenant_url = f"sqlite+aiosqlite:///{tenant_db_file}"
        # Create the DB file and run migrations (ONLY tenant models)
        tenant_engine_sqlite: AsyncEngine = create_async_engine(tenant_url)
        try:
            async with tenant_engine_sqlite.begin() as conn:
                await conn.run_sync(TenantBase.metadata.create_all)
        finally:
            await tenant_engine_sqlite.dispose()
        logger.info(f"Created SQLite tenant DB: {tenant_db_file}")

        # Optional: auto-seed default payroll spec for new tenants if configured
        from os import getenv

        default_spec = getenv("DEFAULT_PAYROLL_SPEC_YML")
        if default_spec:
            try:
                from scripts.seed_payroll_spec import seed_payroll_spec
                import asyncio

                asyncio.create_task(seed_payroll_spec(company_id, default_spec))
            except Exception:  # pragma: no cover - operational
                logger.exception("Failed to seed default payroll spec for %s", company_id)
        return tenant_db_file

    else:
        # For other DBs, just return the base DB name (no per-tenant DB)
        base_db_name = DATABASE_URL.rsplit("/", 1)[-1]
        logger.info("Skipping tenant DB creation for non-Postgres/SQLite DB: %s", DATABASE_URL)
        return base_db_name
