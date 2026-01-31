#!/usr/bin/env python3
"""
Seed categories into a tenant DB from a YAML file.
Usage:
    python scripts/seed_categories.py --company-id 1 --yml seed/categories/default_categories.yml
"""
import argparse
import os
import sys
import yaml
import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


def load_yaml(path: str):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def upsert_categories(db_path: str, categories: list[dict]) -> None:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        # First pass: ensure all codes exist
        for c in categories:
            code = c.get("code")
            name = c.get("name")
            is_expense = 1 if c.get("is_expense") else 0
            is_income = 1 if c.get("is_income") else 0
            comment = c.get("comment")
            if code:
                cur.execute(
                    "SELECT id FROM categories WHERE code = ?",
                    (code,)
                )
                row = cur.fetchone()
                if row:
                    cur.execute(
                        "UPDATE categories SET name=?, is_expense=?, is_income=?, comment=? WHERE code=?",
                        (name, is_expense, is_income, comment, code),
                    )
                else:
                    cur.execute(
                        "INSERT INTO categories (code, name, is_expense, is_income, comment) VALUES (?, ?, ?, ?, ?)",
                        (code, name, is_expense, is_income, comment),
                    )
            else:
                # fallback: upsert by name
                cur.execute("SELECT id FROM categories WHERE name = ?", (name,))
                row = cur.fetchone()
                if row:
                    cid = row[0]
                    cur.execute(
                        "UPDATE categories SET is_expense=?, is_income=?, comment=? WHERE id=?",
                        (is_expense, is_income, comment, cid),
                    )
                else:
                    cur.execute(
                        "INSERT INTO categories (name, is_expense, is_income, comment) VALUES (?, ?, ?, ?)",
                        (name, is_expense, is_income, comment),
                    )
        conn.commit()
        # Second pass: set parent_id where given
        code_to_id = {}
        for row in cur.execute("SELECT id, code FROM categories").fetchall():
            code_to_id[row[1]] = row[0]
        for c in categories:
            code = c.get("code")
            parent = c.get("parent")
            if not code or not parent:
                continue
            parent_id = code_to_id.get(parent)
            if not parent_id:
                logger.warning("Parent code %s not found; skipping parent for %s", parent, code)
                continue
            cur.execute("UPDATE categories SET parent_id = ? WHERE code = ?", (parent_id, code))
        conn.commit()
    finally:
        conn.close()


def validate_categories_spec(obj: dict) -> None:
    if not obj or not isinstance(obj, dict):
        raise ValueError("Spec must be a mapping with a 'categories' key")
    if "categories" not in obj:
        raise ValueError("Missing 'categories' key in spec")
    if not isinstance(obj["categories"], list):
        raise ValueError("'categories' must be a list of category entries")


def seed_categories(company_id: int, yml_path: str) -> None:
    db_path = f".local/company_{company_id}.db"
    if not os.path.exists(db_path):
        logger.error("DB %s does not exist; run migrations first", db_path)
        sys.exit(1)
    obj = load_yaml(yml_path)
    validate_categories_spec(obj)
    cats = obj["categories"]
    upsert_categories(db_path, cats)
    logger.info("Seeded %s categories into company %s", len(cats), company_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--company-id", type=int, required=True)
    parser.add_argument("--yml", type=str, required=True)
    args = parser.parse_args()
    seed_categories(args.company_id, args.yml)
