#!/usr/bin/env python3
"""Stub: iterate configured tenants and run migrations (placeholder)."""

def main() -> None:
    # TODO: load tenant list from config or common DB
    tenants = ["example_tenant"]
    import logging

    logger = logging.getLogger(__name__)
    for t in tenants:
        logger.info("STUB: migrate tenant %s", t)


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    main()
