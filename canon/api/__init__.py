"""API package for FastAPI routers.

We create a minimal healthcheck router as a starting point.
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session

router = APIRouter()


@router.get("/health")
async def health(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, str]:
    # Basic DB connectivity check; can be extended
    from sqlalchemy import text

    await session.execute(text("SELECT 1"))
    return {"status": "ok"}
