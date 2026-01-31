#!/usr/bin/env python3
"""
Add a `code` column to `categories` table in tenant DBs if missing.
"""
import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


def tenant_db_paths():
    p = Path(".local")
    return sorted([x for x in p.glob("company_*.db") if x.is_file()])


def table_columns(db_path: str, table: str):
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(f"PRAGMA table_info('{table}')")
        return [row[1] for row in cur.fetchall()]
    finally:
        conn.close()


def add_column(db_path: str, column_def: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(f"ALTER TABLE categories ADD COLUMN {column_def}")
        conn.commit()
    finally:
        conn.close()


def main() -> None:
    dbs = tenant_db_paths()
    if not dbs:
        logger.info("No tenant DBs found in .local/")
        return
    for db in dbs:
        try:
            cols = table_columns(db, "categories")
            if "code" not in cols:
                logger.info("Adding 'code' column to categories in %s", db)
                add_column(db, "code TEXT")
            else:
                logger.info("'code' already present in %s", db)
        except Exception:
            logger.exception("Failed processing %s", db)

    logger.info("Done.")


if __name__ == "__main__":
    main()
