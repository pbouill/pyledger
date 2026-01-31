#!/usr/bin/env python3
"""Run a minimal schema migration for all tenant databases.

This is intentionally small and focused: it applies additive migrations
(such as adding a new column) that are safe to run multiple times.

Usage:
  ./scripts/migrate_tenants.py

It reads the main DATABASE_URL (via canon.config.get_database_url()) to
locate the primary DB, enumerates companies, and runs tenant-level SQL to
bring tenant DBs up to date.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Iterable

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from canon.config import get_database_url

logger = logging.getLogger(__name__)


async def _connect_engine(url: str) -> AsyncEngine:
    # Ensure asyncpg driver for Postgres URLs
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://")
    return create_async_engine(url)


async def _tenant_urls_from_main(db_url: str, company_ids: Iterable[int]) -> list[str]:
    """Given the main DB url and company ids, construct tenant DB URLs.

    This follows the same naming convention used by
    :func:`canon.util.tenant.create_company_database`.
    """
    # For postgres-style URLs return URLs of the tenant DBs on same host
    if db_url.startswith("postgresql://"):
        async_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
        base = async_url.rsplit("/", 1)[0]
        base_db_name = db_url.rsplit("/", 1)[-1]
        return [f"{base}/{base_db_name}_company_{cid}" for cid in company_ids]

    # For sqlite-style DBs, tenant DBs aren't created; return empty list
    return []


async def apply_opening_balance_migration(engine: AsyncEngine) -> None:
    """Apply the opening_balance additive migration to a tenant DB."""
    async with engine.begin() as conn:
        # Detect dialect
        dialect_name = engine.dialect.name
        if dialect_name == "postgresql":
            logger.info("Applying Postgres migration: add opening_balance")
            await conn.execute(
                text(
                    "ALTER TABLE account ADD COLUMN IF NOT EXISTS "
                    "opening_balance double precision NOT NULL DEFAULT 0.0"
                )
            )
        elif dialect_name == "sqlite":
            logger.info("Applying SQLite migration: add opening_balance if missing")
            res = await conn.execute(text("PRAGMA table_info('account')"))
            cols = [r[1] for r in res.fetchall()]
            if "opening_balance" not in cols:
                await conn.execute(
                    text(
                        "ALTER TABLE account ADD COLUMN "
                        "opening_balance REAL DEFAULT 0.0"
                    )
                )
        else:
            logger.warning(
                "Unknown dialect %s — skipping tenant migration",
                dialect_name,
            )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    db_url = get_database_url()
    logger.info("Using main DB URL: %s", db_url)

    # Connect to main DB
    main_engine = await _connect_engine(db_url)

    try:
        async with main_engine.begin() as conn:
            # Collect company ids from main DB (if the table exists)
            try:
                res = await conn.execute(
                    select(text("id")).select_from(text("company"))
                )
                ids = [int(r[0]) for r in res.fetchall()]
            except Exception:
                logger.exception(
                    "Failed to query companies from main DB; aborting tenant migrations"
                )
                return

        tenant_urls = await _tenant_urls_from_main(db_url, ids)
        if not tenant_urls:
            logger.info("No tenant DBs discovered for URL: %s", db_url)
            return

        # Apply migration to each tenant DB
        for url in tenant_urls:
            logger.info("Migrating tenant DB: %s", url)
            eng = await _connect_engine(url)
            try:
                await apply_opening_balance_migration(eng)
                logger.info("Migration applied for %s", url)
            except Exception:
                logger.exception("Failed applying migration for %s", url)
            finally:
                await eng.dispose()

    finally:
        await main_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
