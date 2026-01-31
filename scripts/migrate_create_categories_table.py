#!/usr/bin/env python3
"""
Create `categories` table in tenant DBs (SQLite) if it doesn't exist and
migrate any existing `expense_category` rows into `categories` where applicable.
"""
import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    parent_id INTEGER,
    is_expense BOOLEAN DEFAULT 1,
    is_income BOOLEAN DEFAULT 0,
    comment TEXT,
    FOREIGN KEY(parent_id) REFERENCES categories(id)
);
"""


def tenant_db_paths():
    p = Path(".local")
    return sorted([x for x in p.glob("company_*.db") if x.is_file()])


def table_exists(conn, table: str) -> bool:
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None


def migrate_db(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        if not table_exists(conn, "categories"):
            logger.info("Creating categories table in %s", db_path)
            conn.execute(CREATE_SQL)
            conn.commit()
        # If old table exists, copy rows
        if table_exists(conn, "expense_category") and not table_exists(conn, "categories"):
            logger.info("Migrating expense_category -> categories in %s", db_path)
            conn.execute("INSERT INTO categories (id, name, is_expense) SELECT id, name, 1 FROM expense_category")
            conn.commit()
        # If both exist, avoid duplicate migration; user can handle dedup as needed
    finally:
        conn.close()


def main() -> None:
    dbs = tenant_db_paths()
    if not dbs:
        logger.info("No tenant DBs found in .local/")
        return
    for db in dbs:
        try:
            migrate_db(str(db))
        except Exception:
            logger.exception("Failed processing %s", db)
    logger.info("Done.")


if __name__ == "__main__":
    main()
