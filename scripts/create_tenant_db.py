#!/usr/bin/env python3
"""
Create a tenant SQLite DB at .local/company_{id}.db and run TenantBase.metadata.create_all
"""
import argparse
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from canon.models.tenant import TenantBase

async def create(dbfile: str):
    engine = create_async_engine(f"sqlite+aiosqlite:///{dbfile}")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(TenantBase.metadata.create_all)
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Created tenant DB and ran migrations: %s", dbfile)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--company-id", type=int, required=True)
    args = parser.parse_args()
    dbfile = f".local/company_{args.company_id}.db"
    asyncio.run(create(dbfile))
