"""
Custom SQLAlchemy column type for storing timezones as IANA strings and
deserializing to zoneinfo.ZoneInfo.
"""
import zoneinfo
from typing import Any

from sqlalchemy.types import String, TypeDecorator


class TimezoneType(TypeDecorator):
    """Stores timezones as IANA strings, returns zoneinfo.ZoneInfo on load."""
    impl = String(64)
    cache_ok = True

    def process_bind_param(
        self, value: str | zoneinfo.ZoneInfo | None, dialect: Any
    ) -> str | None:
        if value is None:
            return None
        if isinstance(value, zoneinfo.ZoneInfo):
            return value.key
        if isinstance(value, str):
            return value
        raise TypeError(f"Invalid timezone value: {value!r}")

    def process_result_value(
        self, value: str | None, dialect: Any
    ) -> zoneinfo.ZoneInfo | None:
        if value is None:
            return None
        return zoneinfo.ZoneInfo(value)
