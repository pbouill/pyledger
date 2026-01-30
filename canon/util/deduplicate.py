"""
Generic deduplication utility that finds duplicate rows in a given table based
on a normalization of a target column (e.g., lower(trim(email))).

Features:
- Dry-run (report-only) and apply modes
- Detect referencing foreign keys and update them to point at the canonical row
- Archive duplicate rows into an archive table for recovery
- Per-group transactional apply to keep the DB consistent

Usage (example):
  python -m canon.util.deduplicate --table user --column email --apply

This script is intentionally conservative and includes a dry-run default.
"""
from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List, Optional, Tuple

from sqlalchemy import (
    JSON,
    Column,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    func,
    insert,
    select,
)
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.inspection import inspect

from canon.config import get_database_url

logger = logging.getLogger(__name__)


@dataclass
class DuplicateGroup:
    norm: str
    ids: List[int]
    canonical: int


def get_sync_engine(url: Optional[str] = None) -> Engine:
    if url is None:
        url = get_database_url()
    return create_engine(url)


def reflect_table(engine: Engine, table_name: str) -> Table:
    meta = MetaData()
    tbl = Table(table_name, meta, autoload_with=engine)
    return tbl


def find_duplicate_groups(
    engine: Engine, table_name: str, column: str
) -> List[DuplicateGroup]:
    tbl = reflect_table(engine, table_name)
    col = tbl.c[column]

    with engine.connect() as conn:
        # Find normalized values that appear more than once
        norm_expr = func.lower(func.trim(col))
        q = (
            select(norm_expr.label("norm"), func.count().label("cnt"))
            .group_by(norm_expr)
            .having(func.count() > 1)
        )
        norms = [r[0] for r in conn.execute(q).all()]

        groups: List[DuplicateGroup] = []
        for norm in norms:
            ids_res = conn.execute(
                select(tbl.c.id)
                .where(func.lower(func.trim(col)) == norm)
                .order_by(tbl.c.id)
            )
            ids = [int(r[0]) for r in ids_res.fetchall()]
            if len(ids) > 1:
                canonical = min(ids)
                groups.append(
                    DuplicateGroup(norm=str(norm), ids=ids, canonical=canonical)
                )
    return groups


def find_referencing_fks(engine: Engine, target_table: str) -> List[Tuple[str, str]]:
    """Return list of (ref_table, ref_column) that reference target_table(id).

    Use reflection on each table to ensure we handle DBs (like SQLite) where
    inspector.get_foreign_keys may not expose the details reliably.
    """
    meta = MetaData()
    ref_pairs: List[Tuple[str, str]] = []
    for table_name in inspect(engine).get_table_names():
        tbl = Table(table_name, meta, autoload_with=engine)
        for fk in getattr(tbl, "foreign_keys", set()):
            referred_tbl_name = fk.column.table.name
            referred_col = fk.column.name
            constrained_col = fk.parent.name
            if referred_tbl_name == target_table and referred_col == "id":
                ref_pairs.append((table_name, constrained_col))
    return ref_pairs


def ensure_archive_table(engine: Engine, target_table: str) -> str:
    archive_table = f"{target_table}_dedupe_archive"
    meta = MetaData()
    tbl = Table(
        archive_table,
        meta,
        Column("id", Integer, primary_key=True),
        Column("original_id", Integer, nullable=False),
        Column("original_data", JSON, nullable=False),
        Column("archived_at", String(64), nullable=False),
        Column("group_norm", String(255), nullable=True),
    )
    meta.create_all(engine, tables=[tbl])
    return archive_table


def archive_rows(
    conn: Connection,
    archive_table: str,
    target_table: Table,
    ids: Iterable[int],
    norm: str,
) -> None:
    # Fetch rows and insert JSON representation into archive
    rows = conn.execute(
        select(target_table).where(target_table.c.id.in_(list(ids)))
    ).fetchall()
    for r in rows:
        data = dict(r._mapping)
        conn.execute(
            insert(Table(archive_table, MetaData(), autoload_with=conn.engine)).values(
                original_id=data.get("id"),
                original_data=json.dumps(data),
                archived_at=str(datetime.now(timezone.utc).isoformat()),
                group_norm=norm,
            )
        )


def apply_dedup(
    engine: Engine,
    table_name: str,
    column: str,
    dry_run: bool = True,
    connection: Optional[Connection] = None,
) -> None:
    tbl = reflect_table(engine, table_name)
    groups = find_duplicate_groups(engine, table_name, column)
    if not groups:
        logger.info("No duplicate groups found for %s.%s", table_name, column)
        return

    ref_fks = find_referencing_fks(engine, table_name)
    logger.info("Found %d referencing FKs to update: %s", len(ref_fks), ref_fks)

    archive_table = ensure_archive_table(engine, table_name)
    logger.info("Using archive table: %s", archive_table)

    for g in groups:
        logger.info(
            "Processing group norm=%r ids=%s canonical=%s",
            g.norm,
            g.ids,
            g.canonical,
        )
        duplicates = [i for i in g.ids if i != g.canonical]
        if not duplicates:
            logger.info("No duplicates to remove for group %s", g.norm)
            continue

        # Show planned actions
        logger.info(
            "Planned actions for group %s: update refs %s -> %s, archive %s, delete %s",
            g.norm,
            duplicates,
            g.canonical,
            duplicates,
            duplicates,
        )

        if dry_run:
            continue

        # Apply changes in transaction. If a connection is provided, use it to ensure
        # callers that manage a single connection (e.g., in-memory SQLite tests) can
        # perform dedupe in the same connection scope.
        if connection is not None:
            # Use the provided connection and manage commit/rollback explicitly to
            # avoid starting a nested transaction on an already-used connection.
            conn = connection
            try:
                # Update referencing tables
                for ref_table, ref_col in ref_fks:
                    ref_tbl = Table(ref_table, MetaData(), autoload_with=conn.engine)
                    before = conn.execute(
                        select(ref_tbl).where(ref_tbl.c[ref_col].in_(duplicates))
                    ).fetchall()
                    logger.info(
                        "Rows to update in %s.%s: %s",
                        ref_table,
                        ref_col,
                        before,
                    )

                    res = conn.execute(
                        ref_tbl.update()
                        .where(ref_tbl.c[ref_col].in_(duplicates))
                        .values({ref_col: g.canonical})
                    )
                    try:
                        rc = res.rowcount
                    except Exception:
                        rc = None
                    logger.info("Updated %s rows in %s.%s", rc, ref_table, ref_col)

                    after = conn.execute(
                        select(ref_tbl).where(ref_tbl.c[ref_col].in_([g.canonical]))
                    ).fetchall()
                    logger.info(
                        "Rows now pointing to canonical in %s.%s: %s",
                        ref_table,
                        ref_col,
                        after,
                    )

                # Archive duplicate rows
                archive_rows(conn, archive_table, tbl, duplicates, g.norm)

                # Delete duplicates
                conn.execute(tbl.delete().where(tbl.c.id.in_(duplicates)))

                # Log resulting states within the same connection
                remaining_users = conn.execute(select(tbl)).fetchall()
                logger.info("Remaining rows in %s: %s", table_name, remaining_users)
                for ref_table, _ref_col in ref_fks:
                    ref_tbl = Table(ref_table, MetaData(), autoload_with=conn.engine)
                    ref_rows = conn.execute(select(ref_tbl)).fetchall()
                    logger.info("Rows in %s after delete: %s", ref_table, ref_rows)

                # Commit changes
                try:
                    conn.commit()
                except Exception:
                    conn.rollback()
                    raise
            except Exception:
                logger.exception(
                    "Error applying dedupe for group %s; rolling back",
                    g.norm,
                )
                try:
                    conn.rollback()
                except Exception:
                    pass
                raise
        else:
            with engine.begin() as conn:
                try:
                    for ref_table, ref_col in ref_fks:
                        ref_tbl = Table(
                            ref_table, MetaData(), autoload_with=conn.engine
                        )
                        before = conn.execute(
                            select(ref_tbl).where(ref_tbl.c[ref_col].in_(duplicates))
                        ).fetchall()
                        logger.info(
                            "Rows to update in %s.%s: %s",
                            ref_table,
                            ref_col,
                            before,
                        )

                        res = conn.execute(
                            ref_tbl.update()
                            .where(ref_tbl.c[ref_col].in_(duplicates))
                            .values({ref_col: g.canonical})
                        )
                        try:
                            rc = res.rowcount
                        except Exception:
                            rc = None
                        logger.info("Updated %s rows in %s.%s", rc, ref_table, ref_col)

                        after = conn.execute(
                            select(ref_tbl).where(ref_tbl.c[ref_col].in_([g.canonical]))
                        ).fetchall()
                        logger.info(
                            "Rows now pointing to canonical in %s.%s: %s",
                            ref_table,
                            ref_col,
                            after,
                        )

                    archive_rows(conn, archive_table, tbl, duplicates, g.norm)

                    conn.execute(tbl.delete().where(tbl.c.id.in_(duplicates)))

                    remaining_users = conn.execute(select(tbl)).fetchall()
                    logger.info(
                        "Remaining rows in %s: %s",
                        table_name,
                        remaining_users,
                    )
                    for ref_table, __ref_col in ref_fks:
                        ref_tbl = Table(
                            ref_table, MetaData(), autoload_with=conn.engine
                        )
                        ref_rows = conn.execute(select(ref_tbl)).fetchall()
                        logger.info("Rows in %s after delete: %s", ref_table, ref_rows)

                except Exception:
                    logger.exception(
                        "Error applying dedupe for group %s; rolling back",
                        g.norm,
                    )
                    raise


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generic deduplication helper")
    p.add_argument(
        "--table",
        required=True,
        help="Table to deduplicate (e.g., user)",
    )
    p.add_argument(
        "--column",
        required=True,
        help="Column to use for duplicate detection (e.g., email)",
    )
    p.add_argument(
        "--apply",
        action="store_true",
        help="Perform changes; default is dry-run",
    )
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    logging.basicConfig(level=logging.INFO)
    args = parse_args(argv)
    engine = get_sync_engine()
    logger.info(
        "Connecting to DB and searching for duplicates in %s.%s",
        args.table,
        args.column,
    )
    apply_dedup(engine, args.table, args.column, dry_run=not args.apply)


if __name__ == "__main__":
    main()
