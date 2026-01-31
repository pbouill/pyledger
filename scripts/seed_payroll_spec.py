#!/usr/bin/env python3
"""
Script to seed the payroll_spec table for a company from a YAML file.
Usage:
    python seed_payroll_spec.py --company-id 1 --yml seed/payroll/payroll_spec_canada_ontario_2026.yml

- Loads YAML, inserts as text into the payroll_spec table for the given company.
- Requires the company tenant DB to exist and be migrated.
"""
import argparse
import os
import sys
import yaml
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
import asyncio

logger = logging.getLogger(__name__)


def load_yaml(path):
    with open(path, "r") as f:
        text = f.read()
    try:
        obj = yaml.safe_load(text)
    except Exception as err:
        logger.exception("Failed to parse YAML %s: %s", path, err)
        obj = None
    logger.debug("Loaded YAML %s: %s", path, (text[:200] + '...') if len(text) > 200 else text)
    logger.debug("Parsed object keys: %s", list(obj.keys()) if isinstance(obj, dict) else type(obj))
    return text, obj

def validate_payroll_spec(yml_obj: dict) -> None:
    """Basic validation for required payroll spec fields.

    Expect a structured spec with at least `meta` and `active_date`.
    """
    # Defensive checks with helpful errors
    if yml_obj is None:
        raise ValueError("YAML parsed to None; ensure the file contains valid mapping")
    required = ["meta"]
    missing = [k for k in required if k not in yml_obj]
    if missing:
        raise ValueError(f"Missing required payroll spec keys: {missing}")
    if not isinstance(yml_obj["meta"], dict) or "code" not in yml_obj["meta"]:
        raise ValueError("meta.code is required (e.g., CA-ON-2026)")
    if "active_date" not in yml_obj["meta"] and "active_date" not in yml_obj:
        raise ValueError("active_date is required in meta or top-level (e.g., meta.active_date)")


async def seed_payroll_spec(company_id: int, yml_path: str):
    yml_text, yml_obj = load_yaml(yml_path)

    # Validate structure early to fail fast
    try:
        validate_payroll_spec(yml_obj)
    except Exception as err:
        logger.error("Invalid payroll spec: %s", err)
        sys.exit(1)

    db_path = f".local/company_{company_id}.db"
    if not os.path.exists(db_path):
        logger.error("DB %s does not exist. Run migrations first.", db_path)
        sys.exit(1)
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")

    # Determine jurisdiction and year
    meta = yml_obj.get("meta", {})
    code = meta.get("code")
    jurisdiction = None
    year = None
    if code:
        # Try to parse code like 'CA-ON-2026' -> jurisdiction 'CA-ON', year 2026
        if "-" in code:
            parts = code.rsplit("-", 1)
            jurisdiction = parts[0]
            try:
                year = int(parts[1])
            except Exception:
                year = None
        else:
            jurisdiction = code
    # Fallback to active_date year
    if not year and yml_obj.get("active_date"):
        try:
            year = int(str(yml_obj["active_date"])[:4])
        except Exception:
            year = None

    async with engine.begin() as conn:
        # Check if payroll_spec table exists
        res = await conn.execute(text("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='payroll_spec';
        """))
        if not res.fetchone():
            logger.error("payroll_spec table does not exist. Run migrations.")
            sys.exit(1)

        # Additional meta fields
        currency = meta.get("currency")
        period_mode = meta.get("period_mode")
        active_date_meta = meta.get("active_date") or yml_obj.get("active_date")

        # Upsert: find existing row by jurisdiction+year
        if jurisdiction is None or year is None:
            logger.error("Could not determine jurisdiction or year for payroll spec. Aborting.")
            sys.exit(1)

        # Parse active_date into YYYY-MM-DD if present
        active_date_val = None
        if active_date_meta:
            try:
                from datetime import datetime

                active_date_val = datetime.fromisoformat(str(active_date_meta)).date()
            except Exception:
                active_date_val = None

        # optional human comment from meta.comment
        comment = meta.get("comment")

        res = await conn.execute(text("SELECT id FROM payroll_spec WHERE jurisdiction = :jur AND year = :yr"), dict(jur=jurisdiction, yr=year))
        row = res.fetchone()
        if row:
            spec_id = row[0]
            await conn.execute(
                text(
                    "UPDATE payroll_spec SET spec_yaml = :spec_yaml, code = :code, currency = :currency, period_mode = :period_mode, active_date = :active_date, comment = :comment WHERE id = :id"
                ),
                dict(
                    spec_yaml=yml_text,
                    code=code,
                    currency=currency,
                    period_mode=period_mode,
                    active_date=active_date_val,
                    comment=comment,
                    id=spec_id,
                ),
            )
            logger.info("Updated payroll_spec %s %s (company %s)", jurisdiction, year, company_id)
        else:
            await conn.execute(
                text(
                    "INSERT INTO payroll_spec (year, jurisdiction, spec_yaml, code, currency, period_mode, active_date, comment) VALUES (:year, :jur, :spec_yaml, :code, :currency, :period_mode, :active_date, :comment)"
                ),
                dict(
                    year=year,
                    jur=jurisdiction,
                    spec_yaml=yml_text,
                    code=code,
                    currency=currency,
                    period_mode=period_mode,
                    active_date=active_date_val,
                    comment=comment,
                ),
            )
            logger.info("Inserted payroll_spec %s %s (company %s)", jurisdiction, year, company_id)

# To auto-seed for new companies, call seed_payroll_spec(company_id, default_yml_path) after DB creation/migration.

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--company-id", type=int, required=True)
    parser.add_argument("--yml", type=str, required=True)
    args = parser.parse_args()
    asyncio.run(seed_payroll_spec(args.company_id, args.yml))
