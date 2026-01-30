import logging
from typing import Annotated, Any

import pycountry
from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from pydantic import StrictStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from canon.api.auth import (
    ALGORITHM,
    SECRET_KEY,
    get_user_by_username,
    oauth2_scheme,
)
from canon.db import get_session
from canon.models.base import PydanticBase
from canon.models.company import Company
from canon.models.currency import Currency
from canon.models.user import User
from canon.util.convert import sqlalchemy_to_pydantic

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/company", tags=["company"])

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    if not isinstance(token, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db = session
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not isinstance(username, str):
            raise credentials_exception
    except JWTError as err:
        raise credentials_exception from err
    user = await get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user


class CompanyCreate(PydanticBase):
    name: StrictStr
    legal_name: StrictStr | None = None
    tax_number: StrictStr | None = None
    currency_code: StrictStr | None = None


CompanyResponse = sqlalchemy_to_pydantic(
    Company, name="CompanyResponse"
)  # Dynamic Pydantic model, see CompanyResponse


@router.post("/", response_model=Any)
async def create_company(
    payload: CompanyCreate, user: Annotated[User, Depends(get_current_user)]
) -> Any:
    async for _db in get_session():
        db = _db
        break
    else:
        raise RuntimeError("Could not get DB session")
    result = await db.execute(select(Company).where(Company.name == payload.name))
    if result.first():
        raise HTTPException(status_code=400, detail="Company name already exists")

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

    company = Company(
        name=payload.name,
        legal_name=payload.legal_name or "",
        tax_number=payload.tax_number or "",
        currency_code=currency_code,
        primary_contact_id=user.id,
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)
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


