

from fastapi import APIRouter

from canon.api.auth import router as auth_router
from canon.api.company import router as company_router
from canon.api.currencies import router as currencies_router
from canon.api.health import router as health_router

router = APIRouter()
router.include_router(health_router)
router.include_router(auth_router)
router.include_router(company_router)
router.include_router(currencies_router)
