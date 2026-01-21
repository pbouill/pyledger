"""Tenancy primitives and middleware (single-tenant default).

For now we provide a `SingleTenantResolver` that always returns a default tenant.
Later we'll add SubdomainResolver and an EngineManager that maps tenant -> engine.
"""
from dataclasses import dataclass
from typing import Optional

from fastapi import Request


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


async def get_tenant(request: Request) -> Tenant:
    # Default resolver instance for now
    resolver = SingleTenantResolver()
    tenant = await resolver.resolve(request)
    # Attach to request.state for handlers/middleware that need it
    request.state.tenant = tenant
    return tenant
