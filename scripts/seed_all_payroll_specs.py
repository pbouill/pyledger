#!/usr/bin/env python3
"""Seed all payroll spec YAML files from a directory into a company tenant DB.
Usage:
    python scripts/seed_all_payroll_specs.py --company-id 1 [--dir seed/payroll]

This will skip files named `template.yml`.
"""
import logging
import argparse
from pathlib import Path
import asyncio

from scripts.seed_payroll_spec import seed_payroll_spec

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--company-id", type=int, required=True)
    parser.add_argument("--dir", type=str, default="seed/payroll")
    args = parser.parse_args()
    p = Path(args.dir)
    if not p.exists():
        logger.error("Directory %s does not exist", p)
        return
    tasks = []
    for y in sorted(p.glob("*.yml")):
        if y.name.lower() == "template.yml":
            continue
        tasks.append(seed_payroll_spec(args.company_id, str(y)))
    if tasks:
        async def runner():
            await asyncio.gather(*tasks)

        asyncio.run(runner())
    else:
        logger.info("No spec files found to seed.")

if __name__ == "__main__":
    main()
