import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Awaitable, Callable, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.staticfiles import StaticFiles

from .api import router as api_router
from .api.messages import http_exception_handler
from .db import set_engine
from .migration import migrate_database

"""Application factory for CanonLedger FastAPI app."""

logger = logging.getLogger(__name__)


def create_app(engine: Optional[AsyncEngine] = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        logger.info("Starting up application...")
        migrated_engine = await migrate_database(engine)
        # If a test or caller supplied an engine, register it so internal
        # call-sites that use `get_session()` directly (not via Depends)
        # will use the test engine's sessionmaker.
        if migrated_engine:
            set_engine(migrated_engine)
        yield
        if migrated_engine:
            await migrated_engine.dispose()
        logger.info("Shutting down application...")


    app = FastAPI(
        title="CanonLedger API",
        lifespan=lifespan,
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    # If a caller (e.g., a test) provided an engine, register it immediately
    # so that synchronous call-sites that use `get_session()` directly will
    # use the provided engine even before the lifespan startup runs.
    if engine:
        set_engine(engine)

    # Simple CORS for local dev — tighten for production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    # Register API routes under /api first so they take precedence over
    # serving static files mounted at the root path.
    app.include_router(api_router, prefix="/api")

    # Serve the built frontend (dist -> /app/static in the container)
    # Mount at root so that visiting / returns the static index.html and
    # any client-side routes are handled by the SPA (html=True fallback).
    app.mount(
        "/",
        StaticFiles(directory="static", html=True, check_dir=False),
        name="static",
    )

    # Register a central HTTPException handler that includes message headers

    app.add_exception_handler(HTTPException, http_exception_handler)

    # SPA fallback: serve index.html for any non-API route so client-side
    # routing works (e.g., /login, /company/123). Using an HTTP middleware
    # lets StaticFiles serve real assets and we only return index.html for
    # otherwise-unmatched non-API paths.

    @app.middleware("http")
    async def spa_fallback_middleware(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        resp = await call_next(request)
        path = request.url.path
        if resp.status_code == 404 and not path.startswith("/api") and "." not in path:
            return FileResponse("static/index.html")
        return resp

    return app
