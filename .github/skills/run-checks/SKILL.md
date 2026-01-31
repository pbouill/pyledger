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

CI matrix & DB notes
- Recommend running tests in a matrix that includes `sqlite` (fast, default) and `postgres` (service) to catch DB-specific behaviors such as tenant DB creation and networking issues.
- Use an environment variable (e.g., `CI_DB=postgres|sqlite`) or `DATABASE_URL` to select the backend in CI. Example:
  - Postgres: `DATABASE_URL=postgresql://postgres:postgres@postgres:5432/pyledger`
  - Sqlite: `DATABASE_URL=sqlite+aiosqlite:///:memory:`
- Our `run_checks.sh` already attempts to clear the mypy cache on internal mypy errors; document this behavior in CI so maintainers understand reruns.
- Suggest adding a small pytest marker (e.g., `postgres`) for tenancy/integration tests that should only run in the Postgres job of the matrix.

Continuous improvement
- When a lint, typecheck, or test run fails, the step scripts (`lint.sh`,
  `typecheck.sh`, `test.sh`) will capture the failing tool output into a
  temporary snippet and write a structured candidate file at
  `./.github/skills/run-checks/last_lesson.md` and will exit non-zero. The
  scripts also print a concise candidate lesson to the console for quick
  inspection.
- Implementation detail: the step scripts write the first section of the failing
  tool output to a temp snippet (e.g., `.github/skills/run-checks/_snippet.tmp`)
  and then embed it into `last_lesson.md`. Skills or CI that run `run-checks`
  should ensure the repository working directory is available so these files
  are readable by automated processes.
- The generated candidate is a lightweight, structured snippet describing the
  observed error and a suggested remediation. It is *only* a suggestion and
  **must not** automatically edit `.github/copilot-instructions.md`.
- Suggested workflow:
  1. Run `./.github/skills/run-checks/run_checks.sh` (or `lint.sh`/`typecheck.sh`/`test.sh`).
  2. If a failure occurs, inspect `./.github/skills/run-checks/last_lesson.md` or the
     console output for the structured candidate lesson. CI or the run-checks
     skill should read `last_lesson.md` if present and surface it to reviewers.
  3. If valid, Copilot should prompt the contributor with a concise, DRY suggested
     `docs/Style.md` entry (1–2 sentences plus an optional short incorrect/correct
     example) derived from `./.github/skills/run-checks/last_lesson.md`. The prompt
     should ask whether the contributor would like Copilot to prepare a draft edit
     (branch/commit/PR) or just save the suggestion for manual application. If the
     contributor approves, prepare the draft and present the exact git commands and
     commit message for their confirmation (per Git operations policy).
  4. Re-run `run-checks` until the checks pass.
- Contributors **should not** run `ruff`, `mypy`, or `pytest` directly in place of
  `run-checks` for pre-PR verification; use the `run-checks` skill so the
  structured candidate is produced on failures and the CI behavior is consistent.
- This keeps the process human-reviewed, repeatable, and prevents accidental
  changes to canonical instructions.

Policy note
- Contributors **must** use the `run-checks` skill (or one of the step scripts)
  locally before opening a PR; include a short note in the PR description when
  a `last_lesson.md` suggestion was generated and how it was addressed.
- Updating canonical instructions is a human-reviewed action: propose the change
  in your branch and request maintainer approval before merging.

Scripts
- `lint.sh` — run ruff (`--fix` by default). Usage: `./lint.sh [--no-fix]`
- `typecheck.sh` — run mypy. Usage: `./typecheck.sh [--clear-on-failure] [--force-clear]`
  - `--clear-on-failure`: only attempts automatic mypy cache clearing when an internal mypy error is detected (e.g., a KeyError in mypy internals). This avoids masking normal type errors.
  - `--force-clear`: force cache clearing and re-run mypy even when no internal error is detected (use with caution).
  - When normal type errors occur, the script will print the mypy output location for manual inspection and will not clear cache automatically.
- `test.sh` — run pytest. Usage: `./test.sh`
- `run_checks.sh` — canonical orchestrator; runs lint/type/test. Usage: `./run_checks.sh [--no-fix] [--mypy-only]`

Examples
- Dry run / verification: `.github/skills/run-checks/examples/verify_run_checks.sh` (non-destructive)

Response format
- Report command, exit code, and a 1-line summary of failures if any.
