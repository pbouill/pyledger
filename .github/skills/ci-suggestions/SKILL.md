---
name: "ci-suggestions"
id: "ci-suggestions"
description: "Minimal CI job recommendations to enforce linting, typing, and tests."
triggers:
  - "ci suggestions"
---

# CI suggestions (skill)

Suggested jobs
- `lint`: run `.venv/bin/python -m ruff check .` (or call `./.github/skills/run-checks/lint.sh --no-fix`) and fail on any error.
- `typecheck`: run `.venv/bin/python -m mypy .` (or call `./.github/skills/run-checks/typecheck.sh`) and fail on any error.
- `test`: run `.venv/bin/python -m pytest -q` (or call `./.github/skills/run-checks/test.sh`) and fail on failures.

Implementation note
- Prefer a dedicated job that installs `.venv` and runs the canonical `run-checks` orchestration: `./.github/skills/run-checks/run_checks.sh --no-fix`.

Performance tips
- Cache pip wheels and `.mypy_cache` between runs to speed CI.
- Run `pip install -r requirements.dev.txt` during the install step using the same Python version as CI.
