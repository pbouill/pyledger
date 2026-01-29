# Test-time shim: ensure argon2.__version__ exists to avoid DeprecationWarnings
# emitted by libraries that still access that attribute directly during
# import-time (e.g., passlib's argon2 handler). This keeps tests clean while
# we rely on upstream libraries to adopt importlib.metadata usage.
try:
    import importlib.metadata as _md  # type: ignore
    import argon2 as _argon2  # type: ignore

    if not hasattr(_argon2, "__version__"):
        _ver = _md.version("argon2-cffi")
        if _ver:
            setattr(_argon2, "__version__", _ver)
except Exception:
    # Best-effort only; do not fail test startup if metadata is unavailable.
    pass
