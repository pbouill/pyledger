# Style Guide

**Purpose**: Capture coding and style decisions so the team (and Copilot) follow consistent conventions.

## General project style choices
- Python: target latest stable supported version (recommend: 3.11+).
- Formatting: **Black** for code formatting; **isort** for import sorting.
- Linting: **ruff** or **flake8**. Prefer `ruff` as a fast combined linter/formatter where possible.
- Type checking: **mypy** (basic checks) and lean toward using type hints on public APIs.
- Commit messages: Follow Conventional Commits.
- Pre-commit: add pre-commit hooks to run formatters and linters locally.

## Backend (FastAPI / SQLAlchemy / Postgres)
- Use FastAPI routers split by domain; keep endpoints thin and delegate business logic to service layer.
- Use Pydantic models for request/response schemas; separate DB models and API schemas.
- Use SQLAlchemy 2.0 style (ORM or Core as agreed). Prefer named sessions via DI and explicit transactions.
- Manage DB schema changes with Alembic migrations.

## Frontend (Vue / Vite)
- Vue 3 + Vite.
- Use Composition API and `setup()`-based components.
- State management: Pinia (recommended) or composables.
- Linting: ESLint + Prettier config; prefer TypeScript in components where beneficial.

## Testing
- Backend tests: `pytest`, use test database (e.g., postgres in Docker or a test container); use fixtures for DB setup/teardown.
- Frontend tests: use Vitest and Vue Testing Library.

## Style updates
- **Mandatory**: Any project-wide style choice must be documented in this file with rationale and examples.

---

If you want, I can add a `pyproject.toml`, `pre-commit` config, or sample `ruff`/`mypy` settings to enforce these rules.