#!/usr/bin/env python3
"""
Migrate all rows from the account table in the main app DB (.local/app.db)
to the first company DB (.local/company_1.db), then drop the account table from the main DB.

Usage:
  python scripts/migrate_account_to_company_db.py
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

APP_DB = ".local/app.db"
COMPANY_DB = ".local/company_1.db"

APP_URL = f"sqlite+aiosqlite:///{APP_DB}"
COMPANY_URL = f"sqlite+aiosqlite:///{COMPANY_DB}"

async def migrate_accounts():
    app_engine = create_async_engine(APP_URL)
    company_engine = create_async_engine(COMPANY_URL)

    async with app_engine.begin() as app_conn, company_engine.begin() as company_conn:
        # Check if account table exists in app.db
        res = await app_conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='account'"))
        if not res.fetchone():
            print("No account table found in app.db; nothing to migrate.")
            return
        # Fetch all accounts from app.db
        rows = (await app_conn.execute(text("SELECT * FROM account"))).fetchall()
        if not rows:
            print("No accounts to migrate.")
        else:
            # Get column names
            col_res = await app_conn.execute(text("PRAGMA table_info('account')"))
            columns = [r[1] for r in col_res.fetchall()]
            # Ensure opening_balance is present and set to 0.0 if missing/null
            if "opening_balance" not in columns:
                columns.append("opening_balance")
            col_str = ", ".join(columns)
            qmarks = ", ".join([":" + c for c in columns])
            for row in rows:
                data = dict(zip([c for c in columns if c != "opening_balance"], row))
                if "opening_balance" not in data or data["opening_balance"] is None:
                    data["opening_balance"] = 0.0
                await company_conn.execute(text(f"INSERT INTO account ({col_str}) VALUES ({qmarks})"), data)
            print(f"Migrated {len(rows)} accounts to company_1.db.")
        # Drop account table from app.db
        await app_conn.execute(text("DROP TABLE account"))
        print("Dropped account table from app.db.")
        # Drop currency table from app.db if it exists
        res = await app_conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='currency'"))
        if res.fetchone():
            await app_conn.execute(text("DROP TABLE currency"))
            print("Dropped currency table from app.db.")
    await app_engine.dispose()
    await company_engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate_accounts())
