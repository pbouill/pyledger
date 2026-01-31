import asyncio
import os
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from canon.models.tenant import TenantBase
from canon.models.tenant.account import Account
from canon.models.tenant.expense import Expense
from canon.models.tenant.expense_item import ExpenseItem
from canon.models.tenant.ledger import Ledger, EntryType


DB_PATH = ".local/test_company_expense.db"


@pytest.mark.asyncio
async def test_expense_into_ledger_roundtrip(tmp_path):
    # Ensure clean DB path
    try:
        os.remove(DB_PATH)
    except FileNotFoundError:
        pass

    engine = create_async_engine(f"sqlite+aiosqlite:///{DB_PATH}")
    async with engine.begin() as conn:
        await conn.run_sync(TenantBase.metadata.create_all)

    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        # Create accounts: expense and bank
        expense_acc = Account(name="Office Supplies", institution=None, currency_code="CAD", account_type="expense")
        bank_acc = Account(name="Bank", institution="Test Bank", currency_code="CAD", account_type="asset")
        session.add_all([expense_acc, bank_acc])
        await session.commit()
        await session.refresh(expense_acc)
        await session.refresh(bank_acc)

        # Create an expense with two items (no total set; will be recalculated)
        exp = Expense(project_id=None, employee_id=None, due_date=None, status="submitted", notes="Office supplies purchase")
        session.add(exp)
        await session.flush()
        # Add items
        item1 = ExpenseItem(expense_id=exp.id, value=100.0, tax_rate=0.0, expense_category_id=None, description="Notebooks", is_remittance=False)
        item2 = ExpenseItem(expense_id=exp.id, value=50.0, tax_rate=0.0, expense_category_id=None, description="Ink cartridges", is_remittance=False)
        session.add_all([item1, item2])
        await session.commit()

        # Recalculate expense total from items
        await exp.recalculate_total(session)
        await session.commit()

        # Create ledger entries representing the expense: debit expense account, credit bank
        debit = Ledger(account_id=expense_acc.id, amount=exp.total, description="Expense: Office supplies", related_expense_id=exp.id, entry_type=EntryType.expense)
        credit = Ledger(account_id=bank_acc.id, amount=-exp.total, description="Paid by bank", related_expense_id=exp.id, entry_type=EntryType.expense)
        session.add_all([debit, credit])
        await session.commit()

        # Assertions
        res = await session.execute(select(Expense).where(Expense.id == exp.id))
        exp_row = res.scalar_one_or_none()
        assert exp_row is not None
        assert abs((exp_row.total or 0.0) - 150.0) < 0.001

        lres = await session.execute(select(Ledger).where(Ledger.related_expense_id == exp.id))
        ledger_rows = lres.scalars().all()
        assert len(ledger_rows) == 2
        total = sum(r.amount for r in ledger_rows)
        # Ledger should balance to zero for the expense
        assert abs(total) < 0.001

        # Company trial balance should reflect the account balances
        from canon.util.ledger import company_trial_balance

        tb = await company_trial_balance(session)
        # expense account should have positive balance equal to expense total
        assert abs(tb.get(expense_acc.id, 0.0) - exp.total) < 0.001
        # bank account should have negative balance equal to -expense total
        assert abs(tb.get(bank_acc.id, 0.0) + exp.total) < 0.001

    await engine.dispose()
