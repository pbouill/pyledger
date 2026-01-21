# TODO: Migrations, CI, Tenant provisioning, and Dev notes

This TODO lists deferred work around database migrations, CI validation, tenant provisioning, and dev workflows. It documents decisions to postpone implementing Alembic and CI now, but describes recommended tools, scripts, and checks so we can implement them later with minimal rework. 🔧

---

## What is Alembic? 💡

- **Alembic** is the standard migrations tool used with SQLAlchemy. It records schema changes as versioned scripts and can apply or revert schema changes reliably.
- We defer adding Alembic now, but we should define how we'll use it before writing migrations.

---

## Proposed migration strategy (high level)

- **Dual Alembic environments**:
  - `alembic/common` — migrations for the shared/common DB (companies, currencies, tax rates).
  - `alembic/tenant` — migrations for tenant databases (dynamic DB URL per run).
- **Scripts (placeholders in `pyledger/scripts/`)**:
  - `create-tenant-db <name>` — provision DB/user (dev stub; production uses IaC/cloud APIs).
  - `migrate-tenant <name>` — run tenant Alembic env against one DB.
  - `migrate-all` — iterate all tenants and run `migrate-tenant`.
  - `bootstrap-tenant <name>` — create DB, run migrations, seed defaults, register in common DB.
  - `seed-tenant <name>` — seed default chart of accounts, currencies, and demo data.

---

## CI checklist (deferred, to implement later)

- Linting: `ruff`/`black`/`isort`.
- Type checking: `mypy`.
- Unit tests: `pytest`.
- Migration validation job:
  - Bring up ephemeral Postgres (single instance for dev) and create sample tenant DBs (e.g., `tenant_acme`, `tenant_foo`).
  - Run `migrate-tenant` / `migrate-all` against these DBs.
  - Run a quick smoke test to ensure app can connect and CRUD basic models.
  - Run `alembic downgrade -1` to validate rollback for reversible migrations (where applicable).
- Add migration validation to `.github/workflows/ci.yml` once Alembic is introduced.

---

## Dev environment notes

- Create `docker-compose.override.dev.yml` that:
  - Starts Postgres and optionally `pgbouncer`.
  - Optionally pre-creates sample tenant DBs for local dev.
  - Mounts secrets files consistent with `pyledger/config.py` behavior (secret-file first, env fallback).
- For local testing, a single Postgres instance can host common DB + multiple tenant DBs.

> Important: Use `pyledger/config.py` secret-file pattern for DB passwords to keep parity with production secret handling.

---

## Migration safety & rollback guidance

- Always snapshot/backup tenant DB before running destructive migrations in production.
- Prefer small, reversible migrations; if data migrations are needed, include explicit scripts and test them in CI.
- Maintain an `alembic_version` table per tenant DB and check consistency during `migrate-all`.

---

## Tests to add later

- Integration tests: spin up ephemeral DB(s), run migrations, seed data, run API smoke tests.
- Migration tests: `upgrade head` + `downgrade -1` on a fresh DB to ensure migration and rollback paths work.

---

## Priorities / Minimal next tasks (short list) ✔️
1. Add `docs/TODO.md` (this file).
2. Add script stubs in `pyledger/scripts/`: `bootstrap-tenant.py`, `migrate-tenant`, `migrate-all`.
3. Scaffold backend minimal files in `pyledger/`: `main.py`, `db.py`, `tenancy.py`, `models/__init__.py` (placeholders).
4. Add frontend scaffold in `./app/` with `package.json` and basic Vite+Vue starter.
5. Add `docker-compose.override.dev.yml` to create dev DB(s) and document usage.

---

## Callouts

- We can postpone Alembic and CI implementation, but document the exact expected scripts and CI checks now so the future implementation is straightforward.
- Design abstractions now (TenantResolver, EngineManager) to avoid coupling the app to a single global DB later.

---

*Generated on 2026-01-21 by project scaffold notes.*
