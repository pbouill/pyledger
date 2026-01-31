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
    """Return a database connection URL.

    Resolution order:
    1. `DATABASE_URL` env var (explicit override)
    2. If `DB_TYPE=sqlite` then use `DB_PATH` or default `./dev.db`
    3. Otherwise construct a Postgres URL from env/secrets (backwards compatible)

    This makes it easy to opt into a local sqlite dev mode without changing
    production / compose settings.
    """
    # 1) Explicit override
    explicit = os.getenv("DATABASE_URL")
    if explicit:
        return explicit

    # 2) Optional sqlite dev mode
    db_type = os.getenv("DB_TYPE", "postgres").lower()
    if db_type == "sqlite":
        db_path = os.getenv("DB_PATH", ".local/")
        # Always use app.db as the main DB file in the specified directory
        if not db_path.endswith("/"):
            db_path += "/"
        db_file = f"{db_path}app.db"
        return f"sqlite+aiosqlite:///{db_file}"

    # 3) Default Postgres (existing behavior)
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
