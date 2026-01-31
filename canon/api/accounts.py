import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import StrictStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from canon.api.auth import get_current_user
from canon.db import get_session
from canon.enums.account import AccountType
from canon.models.account import Account
from canon.models.account_transaction import AccountTransaction
from canon.models.base import PydanticBase
from canon.models.company import Company
from canon.models.user import User
from canon.models.user_permission import UserPermission
from canon.tenancy import engine_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/company/{company_id}/accounts", tags=["accounts"])


class AccountCreate(PydanticBase):
    name: StrictStr
    institution: StrictStr | None = None
    currency_code: StrictStr | None = None
    account_type: AccountType
    opening_balance: float | None = 0.0


class AccountOut(PydanticBase):
    id: int
    name: str
    institution: str | None
    currency_code: str | None
    account_type: AccountType
    opening_balance: float | None = 0.0


class TransactionCreate(PydanticBase):
    amount: float
    description: StrictStr | None = None


class TransactionOut(PydanticBase):
    id: int
    account_id: int
    amount: float
    currency_code: str | None
    description: str | None


class AccountUpdate(PydanticBase):
    name: StrictStr | None = None
    institution: StrictStr | None = None
    currency_code: StrictStr | None = None
    account_type: AccountType | None = None
    opening_balance: float | None = None


async def ensure_company_and_permission(
    company_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    require_write: bool = False,
) -> Company:
    result = await session.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    if company.primary_contact_id == user.id:
        return company

    r = await session.execute(
        select(UserPermission).where(
            (UserPermission.company_id == company_id)
            & (UserPermission.user_id == user.id)
        )
    )
    perm = r.scalar_one_or_none()
    if perm is None:
        raise HTTPException(status_code=403, detail="Forbidden")
    if require_write and not perm.permission.can_write():
        raise HTTPException(status_code=403, detail="Forbidden")
    return company


@router.get("/", response_model=list[AccountOut])
async def list_accounts(
    company_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Any:
    await ensure_company_and_permission(company_id, user, session)
    logger.debug(f"Fetching accounts for company_id={company_id} using tenant DB session.")
    async with engine_manager.get_session_for_company(company_id) as tenant_session:
        # Log the DB URL for the session's engine
        db_url = str(tenant_session.bind.url) if tenant_session.bind else None
        logger.debug(f"Tenant session DB URL: {db_url}")
        res = await tenant_session.execute(select(Account))
        accounts = list(res.scalars().all())
        logger.debug(f"Fetched {len(accounts)} accounts for company_id={company_id}")
        return [AccountOut.model_validate(a) for a in accounts]


@router.post("/", response_model=AccountOut)
async def create_account(
    company_id: int,
    payload: AccountCreate,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Any:
    await ensure_company_and_permission(
        company_id, user, session, require_write=True
    )
    async with engine_manager.get_session_for_company(company_id) as tenant_session:
        acct = Account(
            name=payload.name,
            institution=payload.institution,
            currency_code=payload.currency_code,
            account_type=payload.account_type,
            opening_balance=payload.opening_balance or 0.0,
        )
        tenant_session.add(acct)
        await tenant_session.commit()
        await tenant_session.refresh(acct)
        return AccountOut.model_validate(acct)


@router.get("/{account_id}/transactions", response_model=list[TransactionOut])
async def list_transactions(
    company_id: int,
    account_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Any:
    await ensure_company_and_permission(company_id, user, session)
    async with engine_manager.get_session_for_company(company_id) as tenant_session:
        res = await tenant_session.execute(
            select(AccountTransaction).where(
                AccountTransaction.account_id == account_id
            )
        )
        txs = list(res.scalars().all())
        # Ensure transactions do not expose currency separately — it's provided for
        # convenience but is derived from account's currency.
        return [TransactionOut.model_validate(t) for t in txs]


@router.get("/summary", response_model=list[dict])
async def accounts_summary(
    company_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Any:
    await ensure_company_and_permission(company_id, user, session)
    async with engine_manager.get_session_for_company(company_id) as tenant_session:
        # Sum transactions per account and add opening_balance
        res = await tenant_session.execute(
            select(Account.id, Account.opening_balance)
        )
        acc_rows = res.all()

        # Gather sums of transactions per account
        sums = {}
        r2 = await tenant_session.execute(
            select(
                AccountTransaction.account_id,
                func.coalesce(func.sum(AccountTransaction.amount), 0.0),
            ).group_by(AccountTransaction.account_id)
        )
        for aid, total in r2.all():
            sums[aid] = float(total or 0.0)

        result: list[dict] = []
        for aid, opening in acc_rows:
            curr = float(opening or 0.0) + float(sums.get(aid, 0.0))
            result.append({"account_id": aid, "current_balance": curr})
        return result

@router.get("/types", response_model=list[str])
async def account_types(
    company_id: int,
    user: Annotated[User, Depends(get_current_user)],
) -> Any:
    # No need to check company-level permissions for this read-only list
    return [t.value for t in AccountType]


@router.post("/{account_id}/transactions", response_model=TransactionOut)
async def create_transaction(
    company_id: int,
    account_id: int,
    payload: TransactionCreate,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Any:
    await ensure_company_and_permission(
        company_id, user, session, require_write=True
    )
    async with engine_manager.get_session_for_company(company_id) as tenant_session:
        # Ensure transaction currency matches the account currency.
        # Transactions do not accept a currency_code in the payload.
        res = await tenant_session.execute(
            select(Account).where(Account.id == account_id)
        )
        acct = res.scalar_one_or_none()
        if acct is None:
            raise HTTPException(status_code=404, detail="Account not found")
        tx = AccountTransaction(
            account_id=account_id,
            amount=payload.amount,
            currency_code=acct.currency_code,
            description=payload.description,
        )
        tenant_session.add(tx)
        await tenant_session.commit()
        await tenant_session.refresh(tx)
        return TransactionOut.model_validate(tx)


@router.patch("/{account_id}", response_model=AccountOut)
async def update_account(
    company_id: int,
    account_id: int,
    payload: AccountUpdate,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Any:
    await ensure_company_and_permission(
        company_id, user, session, require_write=True
    )
    async with engine_manager.get_session_for_company(company_id) as tenant_session:
        res = await tenant_session.execute(
            select(Account).where(
                Account.id == account_id
            )
        )
        acct = res.scalar_one_or_none()
        if acct is None:
            raise HTTPException(status_code=404, detail="Account not found")
        if payload.name is not None:
            acct.name = payload.name
        if payload.institution is not None:
            acct.institution = payload.institution
        if payload.currency_code is not None:
            acct.currency_code = payload.currency_code
        if payload.account_type is not None:
            acct.account_type = payload.account_type
        if payload.opening_balance is not None:
            acct.opening_balance = payload.opening_balance
        await tenant_session.commit()
        await tenant_session.refresh(acct)
        return AccountOut.model_validate(acct)
