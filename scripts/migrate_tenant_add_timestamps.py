#!/usr/bin/env python3
"""
Add `created_at` and `updated_at` DATETIME columns to tenant DB tables if missing.
This is intended for local/dev SQLite tenant DBs in `.local/company_{id}.db`.
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


def add_column_if_missing(db_path: str, table: str, coldef: str, colname: str):
    cols = table_columns(db_path, table)
    if colname in cols:
        logger.debug("%s already has column %s", table, colname)
        return False
    conn = sqlite3.connect(db_path)
    try:
        logger.info("Adding column %s to %s in %s", colname, table, db_path)
        # Use a plain column def without non-constant defaults to remain compatible
        # with SQLite ALTER TABLE limitations, then backfill values where needed.
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {coldef}")
        conn.commit()
        # If we just added created_at, backfill with CURRENT_TIMESTAMP for existing rows
        if colname == "created_at":
            try:
                conn.execute(f"UPDATE {table} SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
                conn.commit()
            except Exception:
                logger.exception("Failed to backfill created_at for %s in %s", table, db_path)
        return True
    finally:
        conn.close()


def main() -> None:
    dbs = tenant_db_paths()
    if not dbs:
        logger.info("No tenant DBs found in .local/")
        return
    for db in dbs:
        try:
            tables = []
            conn = sqlite3.connect(db)
            try:
                cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [r[0] for r in cur.fetchall()]
            finally:
                conn.close()

            for t in tables:
                # Skip sqlite internal tables
                if t.startswith("sqlite_"):
                    continue
                add_column_if_missing(str(db), t, "created_at DATETIME", "created_at")
                add_column_if_missing(str(db), t, "updated_at DATETIME", "updated_at")
        except Exception:
            logger.exception("Failed processing %s", db)

    logger.info("Done.")


if __name__ == "__main__":
    main()
