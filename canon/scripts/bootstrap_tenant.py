#!/usr/bin/env python3
"""Bootstrap tenant DB (placeholder).

Creates database and runs migrations; implemented later per `docs/TODO.md`.
"""

import argparse
import logging

logger = logging.getLogger(__name__)


def main() -> None:
    p = argparse.ArgumentParser(description="Bootstrap a tenant (placeholder)")
    p.add_argument("name", help="Tenant name")
    args = p.parse_args()
    logger.info("STUB: bootstrap tenant %s", args.name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
