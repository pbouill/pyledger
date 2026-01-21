#!/usr/bin/env python3
"""Check repository quality: run ruff and mypy.

Usage: ./pyledger/scripts/check_repo.py [--fix]
Exits with non-zero code if any check fails. If `--fix` is provided, the script will
show the planned fix commands and ask for confirmation before applying them.
"""
from __future__ import annotations

import logging
import subprocess
import sys
from typing import Sequence


def run(cmd: Sequence[str]) -> int:
    logging.info("$ %s", " ".join(cmd))
    res = subprocess.run(cmd)
    return res.returncode


def gather_checks() -> list[tuple[list[str], str]]:
    return [
        (["ruff", "check", ".", "--select", "E,F,I,T,B,Q"], "ruff"),
        (["mypy", "pyledger", "tests"], "mypy"),
    ]


def gather_fix_commands() -> list[list[str]]:
    # The exact fix commands we would run if the user confirms.
    return [
        ["ruff", "check", ".", "--fix"],
        ["isort", "."],
        ["black", "."],
    ]


def prompt_yes_no(prompt: str) -> bool:
    try:
        ans = input(prompt + " [y/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return ans in ("y", "yes")


def main() -> None:
    checks = gather_checks()
    rc = 0

    for cmd, name in checks:
        logging.info("Running %s...", name)
        r = run(cmd)
        if r != 0:
            logging.error("%s reported issues (exit code %s).", name, r)
            rc = r if rc == 0 else rc
        else:
            logging.info("%s OK", name)

    if rc != 0 and "--fix" in sys.argv:
        fixes = gather_fix_commands()
        logging.info("\nPlanned fix commands:")
        for f in fixes:
            logging.info("  $ %s", " ".join(f))

        # Confirm with the user before applying fixes
        if not prompt_yes_no("Apply the above fixes now?"):
            logging.info(
                "Aborting fixes. Review the reported issues and "
                "run the script with --fix to retry."
            )
            sys.exit(rc)

        for f in fixes:
            logging.info("Running fix: %s", " ".join(f))
            r = run(f)
            if r != 0:
                logging.error("Fix command %s failed with exit code %s", " ".join(f), r)
                sys.exit(r)

        # Re-run checks after fixes
        logging.info("Re-running checks after fixes...")
        main()
        return

    if rc != 0:
        logging.error("One or more checks failed. See output above for details.")
    sys.exit(rc)


if __name__ == "__main__":
    main()
