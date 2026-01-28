---
name: "ci-suggestions"
id: "ci-suggestions"
description: "Minimal CI job recommendations to enforce linting, typing, and tests."
triggers:
  - "ci suggestions"
---

# CI suggestions (skill)

Suggested jobs
- `lint`: run `ruff check .` and fail on any error.
- `typecheck`: run `mypy .` and fail on any error.
- `test`: run `pytest -q` and fail on failures.

Notes
- Run `install` step with `.venv` tooling or use the pipeline's Python+pip setup.
- Consider caching `.mypy_cache` and pip wheels for speed.
