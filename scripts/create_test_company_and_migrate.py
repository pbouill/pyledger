#!/usr/bin/env python3
"""
Create a test company (if none exists) and run the migration to ensure tenant DB is created and specs seeded.
Usage: python scripts/create_test_company_and_migrate.py
"""
import asyncio
from canon.db import get_engine
from canon.migration import migrate_database
from sqlalchemy import text


async def ensure_company():
    import logging
    logger = logging.getLogger(__name__)
    engine = get_engine()
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT id FROM company LIMIT 1"))
        row = res.fetchone()
        if row:
            logger.info("Existing company id: %s", row[0])
            return row[0]
        # Insert a test company
        await conn.execute(text("INSERT INTO company (name) VALUES (:name)"), {"name": "TestCo"})
        res = await conn.execute(text("SELECT id FROM company WHERE name = :name"), {"name": "TestCo"})
        new = res.fetchone()
        logger.info("Created company id: %s", new[0])
        return new[0]


async def main():
    cid = await ensure_company()
    await migrate_database()

if __name__ == "__main__":
    asyncio.run(main())
