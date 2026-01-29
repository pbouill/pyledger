

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session

router = APIRouter()

@router.get("/health")
async def health(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, str]:
    from sqlalchemy import text
    await session.execute(text("SELECT 1"))
    return {"status": "ok"}


@router.get("/docs/spec")
async def openapi_spec(request: Request) -> dict:
    """Return the generated OpenAPI spec for the API (same as /api/openapi.json)."""
    return request.app.openapi()
