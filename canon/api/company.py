import logging
from typing import Annotated, Any

import pycountry
from fastapi import APIRouter, Depends, HTTPException
from pydantic import StrictStr
from sqlalchemy import select

from canon.api.auth import (
    get_current_user,
)
from canon.db import get_session
from canon.models.base import PydanticBase
from canon.models.company import Company
from canon.models.currency import Currency
from canon.models.user import User
from canon.models.user_permission import UserPermission
from canon.util.convert import sqlalchemy_to_pydantic

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/company", tags=["company"])



class CompanyCreate(PydanticBase):
    name: StrictStr
    legal_name: StrictStr | None = None
    tax_number: StrictStr | None = None
    currency_code: StrictStr | None = None


CompanyResponse = sqlalchemy_to_pydantic(
    Company, name="CompanyResponse"
)  # Dynamic Pydantic model, see CompanyResponse


class CompanyUpdate(PydanticBase):
    name: StrictStr | None = None
    legal_name: StrictStr | None = None
    tax_number: StrictStr | None = None
    currency_code: StrictStr | None = None


@router.post("/", response_model=Any)
async def create_company(
    payload: CompanyCreate, user: Annotated[User, Depends(get_current_user)]
) -> Any:
    async for _db in get_session():
        db = _db
        break
    else:
        raise RuntimeError("Could not get DB session")

    # Re-query the user within our session to avoid relying on a detached
    # ORM instance returned by the auth dependency (prevents visibility/ttl
    # issues across sessions).
    u_res = await db.execute(select(User).where(User.id == user.id))
    db_user = u_res.scalar_one_or_none()
    if db_user is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    result = await db.execute(select(Company).where(Company.name == payload.name))
    if result.first():
        raise HTTPException(status_code=400, detail="Company name already exists")

    # Ensure currency is present or fail early
    currency_code = payload.currency_code
    if currency_code:
        cur_res = await db.execute(
            select(Currency).where(Currency.code == currency_code)
        )
        currency = cur_res.scalar_one_or_none()
        if currency is None:
            # Try to resolve via pycountry and insert minimal Currency record
            try:
                pc = pycountry.currencies.get(alpha_3=currency_code.upper())
                if pc is None:
                    raise KeyError
                currency = Currency(code=pc.alpha_3, name=pc.name, symbol=None)
                db.add(currency)
                await db.commit()
            except Exception as err:
                raise HTTPException(
                    status_code=400, detail="Unknown currency code"
                ) from err

    # Enforce uniqueness for legal_name and tax_number (if provided)
    if payload.legal_name:
        r = await db.execute(
            select(Company).where(Company.legal_name == payload.legal_name)
        )
        if r.first():
            raise HTTPException(status_code=400, detail="Legal name already exists")
    if payload.tax_number:
        r = await db.execute(
            select(Company).where(Company.tax_number == payload.tax_number)
        )
        if r.first():
            raise HTTPException(status_code=400, detail="Tax number already exists")

    # Use the authenticated user's id directly. Using primitive ids avoids
    # cross-session ORM instance problems in our test harness and is stable
    # across different session scopes.
    company = Company(
        name=payload.name,
        legal_name=payload.legal_name or None,
        tax_number=payload.tax_number or None,
        currency_code=currency_code,
        primary_contact_id=user.id,
    )
    db.add(company)
    try:
        await db.commit()
        await db.refresh(company)
    except Exception as err:
        # Convert DB integrity errors into client-friendly 400 responses
        from sqlalchemy.exc import IntegrityError

        await db.rollback()
        if isinstance(err, IntegrityError):
            # Best-effort mapping based on payload values
            if payload.legal_name:
                detail = "Legal name already exists"
                raise HTTPException(
                    status_code=400, detail=detail
                ) from err
            if payload.tax_number:
                detail = "Tax number already exists"
                raise HTTPException(
                    status_code=400, detail=detail
                ) from err
        raise

    # Create per-company tenant database and run migrations. We do this after
    # creating the company row so we can include the `company.id` in the name.
    try:
        from canon.util.tenant import create_company_database

        tenant_db = await create_company_database(company.id)
        logger.info("Created tenant DB for company %s: %s", company.id, tenant_db)
    except Exception as err:  # pragma: no cover - operational
        logger.exception(
            "Failed to create tenant DB for company %s: %s",
            company.id,
            err,
        )
        # Best-effort: do not fail the primary transaction for tenant DB creation.

    return CompanyResponse.model_validate(company)


@router.get("/", response_model=Any)  # Dynamic Pydantic model, see CompanyResponse
async def list_companies(user: Annotated[User, Depends(get_current_user)]) -> Any:
    async for _db in get_session():
        db = _db
        break
    else:
        raise RuntimeError("Could not get DB session")
    result = await db.execute(
        select(Company).where(Company.primary_contact_id == user.id)
    )
    companies = list(result.scalars().all())
    return [CompanyResponse.model_validate(c) for c in companies]


@router.get("/{company_id}/", response_model=Any)
async def get_company(
    company_id: int, user: Annotated[User, Depends(get_current_user)]
) -> Any:
    async for _db in get_session():
        db = _db
        break
    else:
        raise RuntimeError("Could not get DB session")
    res = await db.execute(select(Company).where(Company.id == company_id))
    company = res.scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    # Ensure the user has access (primary contact or a permission entry)
    if company.primary_contact_id != user.id:
        r = await db.execute(
            select(UserPermission).where(
                (UserPermission.company_id == company_id)
                & (UserPermission.user_id == user.id)
            )
        )
        perm = r.scalar_one_or_none()
        if perm is None:
            raise HTTPException(status_code=403, detail="Forbidden")
    return CompanyResponse.model_validate(company)


@router.patch("/{company_id}/", response_model=Any)
async def update_company(
    company_id: int,
    payload: CompanyUpdate,
    user: Annotated[User, Depends(get_current_user)],
) -> Any:
    async for _db in get_session():
        db = _db
        break
    else:
        raise RuntimeError("Could not get DB session")
    res = await db.execute(select(Company).where(Company.id == company_id))
    company = res.scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    if company.primary_contact_id != user.id:
        r = await db.execute(
            select(UserPermission).where(
                (UserPermission.company_id == company_id)
                & (UserPermission.user_id == user.id)
            )
        )
        perm = r.scalar_one_or_none()
        if perm is None or not perm.permission.can_write():
            raise HTTPException(status_code=403, detail="Forbidden")

    # Validate currency if provided
    currency_code = payload.currency_code
    if currency_code:
        cur_res = await db.execute(
            select(Currency).where(Currency.code == currency_code)
        )
        currency = cur_res.scalar_one_or_none()
        if currency is None:
            try:
                pc = pycountry.currencies.get(alpha_3=currency_code.upper())
                if pc is None:
                    raise KeyError
                currency = Currency(code=pc.alpha_3, name=pc.name, symbol=None)
                db.add(currency)
                await db.commit()
            except Exception as err:
                raise HTTPException(
                    status_code=400, detail="Unknown currency code"
                ) from err

    if payload.name is not None:
        company.name = payload.name
    if payload.legal_name is not None:
        company.legal_name = payload.legal_name
    if payload.tax_number is not None:
        company.tax_number = payload.tax_number
    if payload.currency_code is not None:
        company.currency_code = payload.currency_code

    try:
        await db.commit()
        await db.refresh(company)
    except Exception:
        await db.rollback()
        raise

    return CompanyResponse.model_validate(company)


