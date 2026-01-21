"""Configuration helpers for pyledger.

Primary goal: read DB password from Docker secret file when present,
else fall back to environment variable for local dev.

Usage:
    from pyledger.config import get_database_url
    DATABASE_URL = get_database_url()
"""

import os
from typing import Optional


def _read_secret_file(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None


def get_db_password() -> Optional[str]:
    # Check conventional secret file env var first
    secret_paths = [os.getenv("DB_PASSWORD_FILE"), os.getenv("POSTGRES_PASSWORD_FILE")]
    for p in secret_paths:
        if p:
            val = _read_secret_file(p)
            if val:
                return val

    # Fall back to env var (local dev)
    return os.getenv("DB_PASSWORD") or os.getenv("DB_ROOT_PASSWORD")


def get_database_url() -> str:
    """Return a Postgres connection URL constructed from env/secrets.

    Order of precedence for password:
    - secret file
    - `DB_PASSWORD`
    - `DB_ROOT_PASSWORD`
    - none
    """
    user = os.getenv("DB_USER", "postgres")
    host = os.getenv("DB_HOST", "db")
    db = os.getenv("DB_NAME", "pyledger")
    port = os.getenv("DB_PORT", "5432")
    pwd = get_db_password()

    if pwd:
        # NOTE: For security, do NOT log the password.
        # If the URL is used in telemetry, mask the password.
        return f"postgresql://{user}:{pwd}@{host}:{port}/{db}"

    return f"postgresql://{user}@{host}:{port}/{db}"
