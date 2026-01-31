from typing import Dict
from sqlalchemy import select, func
from canon.models.tenant.ledger import Ledger


async def account_balance(session, account_id: int) -> float:
    res = await session.execute(select(func.coalesce(func.sum(Ledger.amount), 0)).where(Ledger.account_id == account_id))
    return float(res.scalar_one())


async def company_trial_balance(session) -> Dict[int, float]:
    """Return mapping account_id -> balance for all ledger entries."""
    res = await session.execute(select(Ledger.account_id, func.coalesce(func.sum(Ledger.amount), 0)).group_by(Ledger.account_id))
    rows = res.fetchall()
    return {row[0]: float(row[1]) for row in rows}
