#!/usr/bin/env python3
"""
Drop the `name` column from `payroll_spec` in tenant SQLite DBs in `.local/`.
This is implemented by recreating the table without the `name` column and
copying data across. It is safe to re-run (will skip if `name` not present).
"""
import logging
import sqlite3
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)


def tenant_db_paths() -> List[Path]:
    p = Path(".local")
    return sorted([x for x in p.glob("company_*.db") if x.is_file()])


def table_info(db_path: str, table: str) -> List[Tuple]:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(f"PRAGMA table_info('{table}')")
        return cur.fetchall()
    finally:
        conn.close()


def recreate_without_name(db_path: str) -> None:
    logger.info("Processing %s", db_path)
    info = table_info(db_path, "payroll_spec")
    cols = [row[1] for row in info]
    if "name" not in cols:
        logger.info("Skipping %s: 'name' column not present", db_path)
        return

    # Build column definitions for new table, preserving types where possible
    col_defs = []
    for cid, name, ctype, notnull, dflt_value, pk in info:
        if name == "name":
            continue
        col = f"{name} {ctype}"
        if pk:
            col += " PRIMARY KEY"
        if notnull:
            col += " NOT NULL"
        if dflt_value is not None:
            col += f" DEFAULT {dflt_value}"
        col_defs.append(col)

    # Ensure the uniqueness constraint on (jurisdiction, active_date)
    col_defs.append("UNIQUE (jurisdiction, active_date)")

    create_sql = f"CREATE TABLE payroll_spec_new ({', '.join(col_defs)});"

    cols_to_copy = [c for c in cols if c != "name"]
    copy_cols_sql = ", ".join(cols_to_copy)

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        logger.info("Creating new table payroll_spec_new in %s", db_path)
        cur.execute("PRAGMA foreign_keys=off;")
        cur.execute(create_sql)
        logger.info("Copying data to new table")
        cur.execute(f"INSERT INTO payroll_spec_new ({copy_cols_sql}) SELECT {copy_cols_sql} FROM payroll_spec;")
        logger.info("Dropping old payroll_spec")
        cur.execute("DROP TABLE payroll_spec;")
        logger.info("Renaming payroll_spec_new to payroll_spec")
        cur.execute("ALTER TABLE payroll_spec_new RENAME TO payroll_spec;")
        cur.execute("PRAGMA foreign_keys=on;")
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
            recreate_without_name(str(db))
        except Exception:
            logger.exception("Failed processing %s", db)
    logger.info("Done.")


if __name__ == "__main__":
    main()
