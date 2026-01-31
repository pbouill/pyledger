#!/usr/bin/env python3
"""
Add a UNIQUE INDEX on (jurisdiction, active_date) for payroll_spec in tenant DBs.
This script is safe to run multiple times; it will use `CREATE UNIQUE INDEX IF NOT EXISTS`.
"""
import logging
import os
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


def tenant_db_path(company_id: int) -> str:
    return f".local/company_{company_id}.db"


def find_tenant_dbs() -> List[Path]:
    p = Path(".local")
    return sorted([x for x in p.glob("company_*.db") if x.is_file()])


def add_unique_index(db_path: str) -> None:
    import sqlite3

    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_payroll_spec_jur_active ON payroll_spec (jurisdiction, active_date)"
        )
        conn.commit()
        logger.info("Ensured unique index on payroll_spec(jurisdiction, active_date) in %s", db_path)
    finally:
        conn.close()


def main() -> None:
    dbs = find_tenant_dbs()
    if not dbs:
        logger.info("No tenant DBs found in .local/")
        return

    for db in dbs:
        try:
            add_unique_index(str(db))
        except Exception:
            logger.exception("Failed to add unique index to %s", db)

    logger.info("Done.")


if __name__ == "__main__":
    main()
