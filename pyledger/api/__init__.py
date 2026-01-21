"""API package for FastAPI routers.

We create a minimal healthcheck router as a starting point.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..tenancy import get_tenant

router = APIRouter()


@router.get("/health")
async def health(session: AsyncSession = Depends(get_session)):
    # Basic DB connectivity check; can be extended
    await session.execute("SELECT 1")
    return {"status": "ok"}
