# Style Guide

**Purpose**: Capture coding and style decisions so the team (and Copilot) follow consistent conventions.

## General project style choices
- Python: target latest stable supported version (recommend: 3.11+).
- Formatting: **Black** for code formatting; **isort** for import sorting.
- Linting: **ruff** or **flake8**. Prefer `ruff` as a fast combined linter/formatter where possible.
- Type checking: **mypy** (basic checks) and lean toward using type hints on public APIs.
- Commit messages: Follow Conventional Commits.
- Pre-commit: add pre-commit hooks to run formatters and linters locally.
- **Logging:** Every Python file should import `logging` and define `logger = logging.getLogger(__name__)` at the module level for consistent logging practices.


## Backend (FastAPI / SQLAlchemy / Postgres)
- Use FastAPI routers split by domain; keep endpoints thin and delegate business logic to service layer.
- Use Pydantic models for request/response schemas; separate DB models and API schemas.
- Use SQLAlchemy 2.0 style (ORM or Core as agreed). Prefer named sessions via DI and explicit transactions.
- Manage DB schema changes with Alembic migrations.
- **Logging:** All backend modules must include `import logging` and `logger = logging.getLogger(__name__)` at the top of the file. Use `logger` for all logging output (not `print`).


## Frontend (Vue / Vite)
- Vue 3 + Vite.
- Use Composition API and `setup()`-based components.
- State management: Pinia (recommended) or composables.
- Linting: ESLint + Prettier config; prefer TypeScript in components where beneficial.
- **UI Library:** Use Google Material Design (e.g., Vuetify or Material Design for Vue) for all UI components to ensure a clean, modern, and accessible interface.
- **Font:** Use Google Nunito as the primary font for all UI text. Import via Google Fonts in the main HTML or CSS entry point.
- **Design:** Prioritize a clean, modern look with ample whitespace, clear visual hierarchy, and responsive layouts. Use Material Design color palette and component guidelines.
- **Documentation:** All major design choices (UI library, font, color palette, layout principles) must be documented here for future contributors.

## Testing
- Backend tests: `pytest`, use test database (e.g., postgres in Docker or a test container); use fixtures for DB setup/teardown.
- Frontend tests: use Vitest and Vue Testing Library.

## Style updates
- **Mandatory**: Any project-wide style choice must be documented in this file with rationale and examples.

---

If you want, I can add a `pyproject.toml`, `pre-commit` config, or sample `ruff`/`mypy` settings to enforce these rules.