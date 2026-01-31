#!/usr/bin/env python3
"""
Add `payroll_tax_deductions` JSON column to tenant `employee` table for existing tenant DBs.
This is a simple migration script for local/dev (SQLite). It will:
 - iterate existing companies from the main DB
 - for each tenant DB (.local/company_{id}.db), check whether the column exists
 - if not, run ALTER TABLE to add the column

Usage:
    python scripts/migrate_add_employee_payroll_tax_deductions.py
"""
import logging
import sqlite3
import os
from pathlib import Path
from typing import List

from sqlalchemy import create_engine, select
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from canon.db import get_engine
from canon.models.company import Company

logger = logging.getLogger(__name__)


def tenant_db_path(company_id: int) -> str:
    return f".local/company_{company_id}.db"


def column_exists(db_path: str, table: str, column: str) -> bool:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(f"PRAGMA table_info('{table}')")
        cols = [row[1] for row in cur.fetchall()]
        return column in cols
    finally:
        conn.close()


def add_column(db_path: str, table: str, column_def: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")
        conn.commit()
    finally:
        conn.close()


async def get_company_ids() -> List[int]:
    engine = await get_engine()
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT id FROM company"))
        return [row[0] for row in res.fetchall()]


def main():
    import asyncio

    ids = asyncio.run(get_company_ids())
    for cid in ids:
        db = tenant_db_path(cid)
        if not os.path.exists(db):
            logger.warning("Skipping company %s: DB %s not found", cid, db)
            continue
        if column_exists(db, "employee", "payroll_tax_deductions"):
            logger.info("Company %s: column exists, skipping", cid)
            continue
        logger.info("Adding payroll_tax_deductions to company %s", cid)
        add_column(db, "employee", "payroll_tax_deductions JSON")

    logger.info("Done.")


if __name__ == "__main__":
    main()
