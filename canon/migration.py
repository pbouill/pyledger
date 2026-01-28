import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncEngine

from .models import Base
from .db import get_engine

logger = logging.getLogger(__name__)

async def migrate_database(engine: Optional[AsyncEngine] = None) -> AsyncEngine:
    """Perform database migrations using SQLAlchemy's metadata."""
    engine = engine or get_engine()
    logger.info("Starting database migration...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database migration completed.")
    return engine
