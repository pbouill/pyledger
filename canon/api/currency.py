import logging

import pycountry
from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/currency", tags=["currency"])


@router.get("", response_model=dict[str, str])
@router.get("/", response_model=dict[str, str])
async def list_currencies() -> dict[str, str]:
    """Return a mapping of ISO alpha_3 currency code to currency name.

    Example: {"USD": "United States dollar", ...}
    """
    result: dict[str, str] = {}
    for c in pycountry.currencies:
        # Prefer attribute access so missing attributes raise AttributeError and
        # are handled explicitly — avoids silent failures.
        try:
            code = c.alpha_3
            name = c.name
        except Exception as err:  # pragma: no cover - defensive
            logger.warning(
                "Currency object missing expected attributes: %r (%s)",
                c,
                err,
            )
            continue

        if code is None or name is None:
            logger.warning(
                "Currency has missing fields; skipping. code=%r name=%r obj=%r",
                code,
                name,
                c,
            )
            continue

        if code in result:
            logger.warning(
                "Duplicate currency code %s (existing=%r new=%r); skipping",
                code,
                result[code],
                name,
            )
            continue

        result[code] = name
    return result
