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
  -m mypy .` once.

Response format
- Report command, exit code, and a 1-line summary of failures if any.
