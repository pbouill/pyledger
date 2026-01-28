import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy import select

from canon.api.auth import (
    ALGORITHM,
    SECRET_KEY,
    get_user_by_username,
    oauth2_scheme,
)
from canon.db import get_session
from canon.models.company import Company
from canon.models.user import User
from canon.util.convert import sqlalchemy_to_pydantic

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/company", tags=["company"])

async def get_current_user(request: Request) -> User:
    token = await oauth2_scheme(request)
    if not isinstance(token, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    async for _db in get_session():
        db = _db
        break
    else:
        raise RuntimeError("Could not get DB session")
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

CompanyResponse = sqlalchemy_to_pydantic(
    Company, name="CompanyResponse"
)  # Dynamic Pydantic model, see CompanyResponse

@router.post("/", response_model=Any)  # Dynamic Pydantic model, see CompanyResponse
async def create_company(
    request: Request,
    name: str,
    legal_name: str = "",
    tax_number: str = "",
    currency_code: str = "",
) -> Any:
    async for _db in get_session():
        db = _db
        break
    else:
        raise RuntimeError("Could not get DB session")
    user = await get_current_user(request)
    result = await db.execute(select(Company).where(Company.name == name))
    if result.first():
        raise HTTPException(status_code=400, detail="Company name already exists")
    company = Company(
        name=name,
        legal_name=legal_name,
        tax_number=tax_number,
        currency_code=currency_code,
        primary_contact_id=user.id,
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return CompanyResponse.model_validate(company)

@router.get("/", response_model=Any)  # Dynamic Pydantic model, see CompanyResponse
async def list_companies(request: Request) -> Any:
    async for _db in get_session():
        db = _db
        break
    else:
        raise RuntimeError("Could not get DB session")
    user = await get_current_user(request)
    result = await db.execute(
        select(Company).where(Company.primary_contact_id == user.id)
    )
    companies = list(result.scalars().all())
    return [CompanyResponse.model_validate(c) for c in companies]
