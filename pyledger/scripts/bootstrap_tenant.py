#!/usr/bin/env python3
"""Stub: bootstrap tenant DB (create DB/user, run migrations, seed defaults, register company).

Placeholder only — implement provisioning and migrations later per docs/TODO.md.
"""

import argparse


def main():
    p = argparse.ArgumentParser(description="Bootstrap a tenant (placeholder)")
    p.add_argument('name', help='Tenant name')
    args = p.parse_args()
    print(f"STUB: bootstrap tenant {args.name}")


if __name__ == '__main__':
    main()
