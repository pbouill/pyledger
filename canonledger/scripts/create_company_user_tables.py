"""Create company and user tables using SQLAlchemy models.

Usage:
    python -m pyledger.scripts.create_company_user_tables
"""
import asyncio

from sqlalchemy.ext.asyncio import AsyncEngine

from canonledger.db import get_engine
from canonledger.models import Base


async def main() -> None:
    engine: AsyncEngine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(main())
