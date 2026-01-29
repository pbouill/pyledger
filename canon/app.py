"""Application factory for CanonLedger FastAPI app."""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.staticfiles import StaticFiles

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

    # Serve the built frontend (dist -> /app/static in the container)
    # Mount at root so that visiting / returns the static index.html and
    # any client-side routes are handled by the SPA (html=True fallback).
    app.mount("/", StaticFiles(directory="static", html=True), name="static")

    # Simple CORS for local dev — tighten for production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.include_router(api_router, prefix="/api")

    # SPA fallback: serve index.html for any non-API route so client-side
    # routing works (e.g., /login, /company/123). Using an HTTP middleware
    # lets StaticFiles serve real assets and we only return index.html for
    # otherwise-unmatched non-API paths.
    from fastapi import Request
    from fastapi.responses import FileResponse

    @app.middleware("http")
    async def spa_fallback_middleware(request: Request, call_next):
        resp = await call_next(request)
        path = request.url.path
        if resp.status_code == 404 and not path.startswith("/api") and "." not in path:
            return FileResponse("static/index.html")
        return resp

    return app
