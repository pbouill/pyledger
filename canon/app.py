"""Application factory for CanonLedger FastAPI app."""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine

from .api import router as api_router
from .migration import migrate_database

logger = logging.getLogger(__name__)


def create_app(engine: Optional[AsyncEngine] = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        logger.info("Starting up application...")
        migrated_engine = await migrate_database(engine)
        yield
        if migrated_engine:
            await migrated_engine.dispose()
        logger.info("Shutting down application...")


    app = FastAPI(title="PyLedger API", lifespan=lifespan)

    # Simple CORS for local dev — tighten for production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.include_router(api_router, prefix="/api")
    return app
