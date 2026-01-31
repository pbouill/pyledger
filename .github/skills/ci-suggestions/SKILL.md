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

CI matrix recommendation
- Add a CI job matrix that runs tests against both sqlite and Postgres to catch DB-specific issues early (e.g., tenant creation and network/database behavior).

Example GitHub Actions snippet (conceptual):

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        db: [sqlite, postgres]
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: pyledger
        ports:
          - 5432:5432
        options: >-
          --health-cmd='pg_isready -U postgres' --health-interval=10s --health-timeout=5s --health-retries=5
    steps:
      - name: Set DATABASE_URL for Postgres
        if: matrix.db == 'postgres'
        run: echo "DATABASE_URL=postgresql://postgres:postgres@postgres:5432/pyledger" >> $GITHUB_ENV
      - name: Set DATABASE_URL for sqlite
        if: matrix.db == 'sqlite'
        run: echo "DATABASE_URL=sqlite+aiosqlite:///:memory:" >> $GITHUB_ENV
      - name: Install deps and run checks
        run: |
          python -m venv .venv
          .venv/bin/python -m pip install --upgrade pip
          .venv/bin/python -m pip install -r requirements.dev.txt
          ./.github/skills/run-checks/run_checks.sh --no-fix
```

- Cache `.mypy_cache` and pip wheels between jobs to speed runs.
- Consider adding a pytest marker (e.g., `postgres`) for tenancy-specific integration tests that should run against Postgres in the matrix.
