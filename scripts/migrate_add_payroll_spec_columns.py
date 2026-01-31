#!/usr/bin/env python3
"""
Add `code`, `currency`, `period_mode`, and `active_date` columns to tenant `payroll_spec` table for existing tenant DBs.
This is a simple migration script for local/dev (SQLite). It will:
 - iterate existing companies from the main DB
 - for each tenant DB (.local/company_{id}.db), check whether the payroll_spec table has the columns
 - if not, run ALTER TABLE to add the columns
 - optionally populate columns from spec_yaml if possible

Usage:
    python scripts/migrate_add_payroll_spec_columns.py
"""
import logging
import sqlite3
import os
from pathlib import Path
from typing import List
import yaml

from sqlalchemy import text
from canon.db import get_engine

logger = logging.getLogger(__name__)


def tenant_db_path(company_id: int) -> str:
    return f".local/company_{company_id}.db"


def table_columns(db_path: str, table: str) -> List[str]:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(f"PRAGMA table_info('{table}')")
        cols = [row[1] for row in cur.fetchall()]
        return cols
    finally:
        conn.close()


def add_column(db_path: str, column_def: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(f"ALTER TABLE payroll_spec ADD COLUMN {column_def}")
        conn.commit()
    finally:
        conn.close()


async def get_company_ids() -> List[int]:
    engine = get_engine()
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT id FROM company"))
        return [row[0] for row in res.fetchall()]


def populate_from_yaml(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute("SELECT id, spec_yaml FROM payroll_spec")
        rows = cur.fetchall()
        for row in rows:
            pid, spec_yaml = row
            try:
                spec = yaml.safe_load(spec_yaml)
            except Exception:
                spec = None
            if spec and isinstance(spec, dict):
                meta = spec.get("meta", {})
                code = meta.get("code")
                currency = meta.get("currency")
                period_mode = meta.get("period_mode")
                comment = meta.get("comment") or spec.get("notes")
                active_date = meta.get("active_date") or spec.get("active_date")
                if active_date:
                    try:
                        from datetime import datetime

                        active_date = datetime.fromisoformat(str(active_date)).date().isoformat()
                    except Exception:
                        active_date = None
                conn.execute(
                    "UPDATE payroll_spec SET code = ?, currency = ?, period_mode = ?, active_date = ?, comment = ? WHERE id = ?",
                    (code, currency, period_mode, active_date, comment, pid),
                )
        conn.commit()
    finally:
        conn.close()


def main() -> None:
    import asyncio

    # Try to get company ids from DB; if that fails (e.g., DB host inaccessible),
    # fall back to scanning local .local/company_{id}.db files.
    try:
        ids = asyncio.run(get_company_ids())
    except Exception:  # pragma: no cover - operational fallback
        logger.warning("Could not query main DB for company ids; falling back to scanning .local/ for tenant DBs")
        ids = []
        for path in sorted(Path(".local").glob("company_*.db")):
            name = path.stem
            try:
                cid = int(name.split("_")[1])
                ids.append(cid)
            except Exception:
                logger.debug("Skipping unknown file in .local: %s", path)

    for cid in ids:
        db = tenant_db_path(cid)
        if not os.path.exists(db):
            logger.warning("Skipping company %s: DB %s not found", cid, db)
            continue
        cols = table_columns(db, "payroll_spec")
        added = False
        if "code" not in cols:
            logger.info("Adding column 'code' to payroll_spec in %s", db)
            add_column(db, "code TEXT")
            added = True
        if "currency" not in cols:
            logger.info("Adding column 'currency' to payroll_spec in %s", db)
            add_column(db, "currency TEXT")
            added = True
        if "period_mode" not in cols:
            logger.info("Adding column 'period_mode' to payroll_spec in %s", db)
            add_column(db, "period_mode TEXT")
            added = True
        if "active_date" not in cols:
            logger.info("Adding column 'active_date' to payroll_spec in %s", db)
            add_column(db, "active_date DATE")
            added = True
        if "comment" not in cols:
            logger.info("Adding column 'comment' to payroll_spec in %s", db)
            add_column(db, "comment TEXT")
            added = True
        if added:
            logger.info("Populating new columns for %s from spec_yaml when possible", db)
            populate_from_yaml(db)
        else:
            logger.info("No changes needed for %s", db)

    logger.info("Done.")


if __name__ == "__main__":
    main()
