#!/usr/bin/env python3
"""Stub: run migrations for a single tenant (placeholder)."""

import argparse


def main():
    p = argparse.ArgumentParser(description="Run migrations for a tenant (placeholder)")
    p.add_argument('name', help='Tenant name')
    args = p.parse_args()
    print(f"STUB: migrate tenant {args.name}")


if __name__ == '__main__':
    main()
