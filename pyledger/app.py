"""Application factory for PyLedger FastAPI app."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router as api_router



import logging
import asyncio
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncEngine
from .db import get_engine
from .models import Base

def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger = logging.getLogger("pyledger.migration")
        engine: AsyncEngine = get_engine()
        logger.info("Checking and migrating database schema (if needed)...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema check/migration complete.")
        yield

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
