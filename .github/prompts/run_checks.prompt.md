# Run lint, typecheck, and tests

Prompt
- Run `ruff`, `mypy`, then `pytest` using the project `.venv` and report outputs.

Template
- `.venv/bin/python -m ruff check .`
- `.venv/bin/python -m mypy .`
- `.venv/bin/python -m pytest -q`

If `mypy` fails, rerun once with cache cleared: `rm -rf .mypy_cache && .venv/bin/python -m mypy .`.

Alternatively, use the helper script: `./scripts/clear_mypy_cache.sh --check` to clear the cache and run `mypy` in one step.

Output
- Return the exit code and the first 5 lines of failing output if any.
