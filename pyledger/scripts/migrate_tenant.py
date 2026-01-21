#!/usr/bin/env python3
"""Stub: run migrations for a single tenant (placeholder)."""

import argparse


def main() -> None:
    p = argparse.ArgumentParser(description="Run migrations for a tenant (placeholder)")
    p.add_argument("name", help="Tenant name")
    args = p.parse_args()
    import logging

    logger = logging.getLogger(__name__)
    logger.info("STUB: migrate tenant %s", args.name)


if __name__ == "__main__":
    main()
