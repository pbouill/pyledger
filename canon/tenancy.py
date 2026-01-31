"""Tenancy primitives and middleware (single-tenant default).

For now we provide a `SingleTenantResolver` that always returns a default tenant.
Later we'll add SubdomainResolver and an EngineManager that maps tenant -> engine.
"""
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncGenerator, Optional

from fastapi import Request
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)


@dataclass
class Tenant:
    id: str
    db_name: Optional[str] = None


class TenantResolver:
    """Interface/protocol for tenant resolution."""

    async def resolve(self, request: Request) -> Tenant:
        raise NotImplementedError


class SingleTenantResolver(TenantResolver):
    """Simple resolver for single-tenant mode.

    Reads a tenant id from environment or defaults to `default`.
    """

    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id

    async def resolve(self, request: Request) -> Tenant:
        # Future: inspect subdomain/header/path to map to tenant
        return Tenant(id=self.tenant_id)


class EngineManager:
    """Manage per-company DB engines and provide tenant sessions.

    Engines are created on demand and cached. Creating an engine will ensure
    the tenant DB exists by delegating to `create_company_database`.
    """

    def __init__(self) -> None:
        self._engines: dict[int, AsyncEngine] = {}

    async def get_engine(self, company_id: int) -> AsyncEngine:
        if company_id in self._engines:
            return self._engines[company_id]

        # If the global app engine is a non-Postgres (e.g., sqlite used in
        # tests), reuse it instead of attempting to create tenant DBs.
        from canon.db import get_engine as _get_global_engine

        global_engine = _get_global_engine()
        if global_engine is not None and "sqlite" in str(global_engine.url):
            self._engines[company_id] = global_engine
            return global_engine

        # Ensure tenant DB exists and run migrations when using Postgres
        from canon.config import get_database_url

        DATABASE_URL = get_database_url()
        async_database_url = DATABASE_URL.replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        base = async_database_url.rsplit("/", 1)[0]
        if DATABASE_URL.startswith("postgresql://"):
            from canon.util.tenant import create_company_database

            # Best-effort: create tenant DB on Postgres backends
            await create_company_database(company_id)
            db_name = DATABASE_URL.rsplit("/", 1)[-1]
            tenant_db = f"{base}/{db_name}_company_{company_id}"
            engine = create_async_engine(tenant_db)
        else:
            # Non-Postgres DB (e.g., sqlite in tests): reuse the main DB URL
            engine = create_async_engine(async_database_url)

        self._engines[company_id] = engine
        return engine


    @asynccontextmanager
    async def get_session_for_company(
        self, company_id: int
    ) -> AsyncGenerator[AsyncSession, None]:
        """Async context manager yielding an AsyncSession for the tenant DB."""
        from sqlalchemy.ext.asyncio import async_sessionmaker

        engine = await self.get_engine(company_id)
        session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

        async with session_maker() as session:  # type: AsyncSession
            yield session

    async def dispose_all(self) -> None:
        for eng in list(self._engines.values()):
            await eng.dispose()
        self._engines.clear()


# Global EngineManager instance
engine_manager = EngineManager()


async def get_tenant(request: Request) -> Tenant:
    # Default resolver instance for now
    resolver = SingleTenantResolver()
    tenant = await resolver.resolve(request)
    # Attach to request.state for handlers/middleware that need it
    request.state.tenant = tenant
    return tenant
