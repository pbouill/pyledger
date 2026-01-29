---
name: "run-checks"
id: "run-checks"
description: "Canonical order and quick fixes for local checks (ruff, mypy, pytest)."
triggers:
  - "run checks"
  - "lint and type check"
prompt_templates:
  - name: "Run full checks"
    file: "../prompts/run_checks.prompt.md"
---

# Run checks (skill)

Purpose
- Provide a reproducible sequence to lint, type-check, and test the project.

Commands (order)
1. `.venv/bin/python -m ruff check .`
2. `.venv/bin/python -m mypy .`  (only clear cache if it fails)
3. `.venv/bin/python -m pytest -q`

Troubleshooting
- If `mypy` reports missing stubs, add the appropriate `types-...` package to
  `requirements.dev.txt` and re-run installs.
- If `mypy` fails for spurious reasons, run `rm -rf .mypy_cache && .venv/bin/python
  -m mypy .` once or use the clear cache helper: `.github/skills/run-checks/clear_mypy_cache.sh --check`.

Scripts
- `lint.sh` — run ruff (`--fix` by default). Usage: `./lint.sh [--no-fix]`
- `typecheck.sh` — run mypy. Usage: `./typecheck.sh [--clear-on-failure]` (if `mypy` fails, this will run the clear-mypy-cache helper once and re-run mypy; it can also attempt to install missing `types-*` packages into `.venv` and update `requirements.dev.txt` automatically)
- `test.sh` — run pytest. Usage: `./test.sh`
- `run_checks.sh` — canonical orchestrator; runs lint/type/test. Usage: `./run_checks.sh [--no-fix] [--mypy-only]`

Examples
- Dry run / verification: `.github/skills/run-checks/examples/verify_run_checks.sh` (non-destructive)

Response format
- Report command, exit code, and a 1-line summary of failures if any.
