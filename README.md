## Internationalization and Validation

This project uses [pycountry](https://pypi.org/project/pycountry/) for ISO 3166-1 country codes, ISO 639 language codes, and ISO 4217 currency codes. All country, language, and currency fields in models are validated using pycountry to ensure correctness and up-to-date standards.

<p align="center">
  <img src="app/src/public/logo.png" alt="PyLedger Logo" width="120" style="border-radius:16px;box-shadow:0 2px 8px rgba(0,0,0,0.08);margin-bottom:1.5rem;" />
</p>

# pyledger

A bookkeeping/accounting application (work in progress).

## Key project docs
- Copilot instructions: `.github/copilot-instructions.md` (canonical) ✅
- Architecture: `docs/Architecture.md` 🔧
- Style: `docs/Style.md` 🎨
- Planned features: `docs/features/` 📋

---

Contributing: see `.github/copilot-instructions.md` for Copilot rules and `docs/` for architecture and style docs.

## Python version (pyenv)

We use `pyenv` to pin a workspace Python version. A `.python-version` file is included with the recommended workspace version.

Recommended setup:

- Install pyenv (see https://github.com/pyenv/pyenv or your platform's package manager).
- Install the workspace Python version:

  ```bash
  pyenv install $(cat .python-version)
  pyenv local $(cat .python-version)
  ```

- To build the Docker image using the workspace version, pass build-args derived from `.python-version`:

  ```bash
  docker build \
    --build-arg PYTHON_VERSION="$(cat .python-version)" \
    --build-arg PYTHON_TAG_SUFFIX="-slim" \
    -t pyledger .
  ```

- Or export environment variables first and use docker-compose which will pass the args to the build:

  ```bash
  export PYTHON_VERSION="$(cat .python-version)"
  export PYTHON_TAG_SUFFIX="-slim"
  docker-compose build
  ```

Note: For local development you may prefer a single-stage `Dockerfile` (easier, larger image) or the current multi-stage build (smaller runtime image). If you want, I can add a `Dockerfile.dev` single-stage variant that is simpler to iterate with.

## Secrets (docker-compose)

This compose file now uses Docker secrets for database passwords. It expects two external secrets to be created:

- `db_root_password` — used by Postgres as `POSTGRES_PASSWORD_FILE`.
- `db_admin_password` — for creating or configuring an additional admin user (optional use by init scripts).

Create them locally with:

```bash
printf "%s" "your_root_password_here" | docker secret create db_root_password -
printf "%s" "your_admin_password_here" | docker secret create db_admin_password -
```

Note: The official Postgres image natively supports `POSTGRES_PASSWORD_FILE` for the initial DB bootstrap. If you want to create an additional admin user at startup using `db_admin_password`, we should add an initialization SQL script (e.g., `docker-entrypoint-initdb.d/01-create-admin.sql`) or a tiny init container that reads `/run/secrets/db_admin_password` and creates the user. I can add the init script if you'd like.

## Using `.env` and secrets together

- Copy `.env.example` → `.env` and edit values for your environment. Keep secrets out of `.env`.
- `docker-compose` will load `.env` and pass values (e.g., `DB_HOST`, `DB_USER`, `DB_NAME`) into the `web` service via `env_file` and explicit `environment` keys.
- The `web` service expects to find the DB password at `/run/secrets/db_root_password` (set as `DB_PASSWORD_FILE=/run/secrets/db_root_password`). For local convenience, you can also set `DB_ROOT_PASSWORD` in your `.env` (not recommended for production). Configure your application to read the secret file first and fall back to the env var. See `pyledger/config.py` which provides `get_database_url()` that follows this pattern.

## Node version (frontend)

We recommend using the current Node LTS (Node 24 as of Jan 2026). You can manage Node locally with `nvm`, `volta`, or another manager and consider adding an `.nvmrc` or `.node-version` file inside `frontend/` to pin the version for contributors.

To build images with a specific Node image tag, pass the `NODE_VERSION` and `NODE_TAG_SUFFIX` build args (defaults: `NODE_VERSION=24`, `NODE_TAG_SUFFIX=-alpine`):

```bash
docker build \
  --build-arg PYTHON_VERSION="$(cat .python-version)" \
  --build-arg PYTHON_TAG_SUFFIX="-slim" \
  --build-arg NODE_VERSION=24 \
  --build-arg NODE_TAG_SUFFIX="-alpine" \
  -t pyledger .
```

Local rapid prototyping (sqlite mode, all runtime files in .local/):

- Set a local sqlite DB: `DB_TYPE=sqlite DB_PATH=.local/dev.db` or use the Makefile helper
- Start the local development runner (backend + frontend):
  - `make dev` (recommended — starts backend and runs `vite build --watch` for auto-built assets in the background). You can also run it via the VS Code task **Dev (make): Start Background (default)**.
  - If you want Vite HMR instead of building to `dist`, use: `make dev-hmr` (starts backend + Vite dev server with HMR) or the VS Code task **Dev (make): Start Background (HMR)**.
  - To run only the backend: `make backend` (runs with --no-frontend)
  - To run with the compose Postgres DB: `./scripts/dev_local.sh --port 8001 --db postgres` or `make dev` with `DB_TYPE=postgres`

Migrations (tenant DBs)

- When adding new tenant-scoped columns (e.g., `opening_balance` on `account`), run:
  - `make migrate-tenants` — this will connect to each tenant DB and apply additive migrations (safe to re-run).
  - The script is `scripts/migrate_tenants.py` and currently applies the `opening_balance` additive migration.

Run frontend unit tests against a running local backend:

- `TEST_API_URL=http://localhost:8001 npm run test:unit -- --run`


Frontend / backend workflows (recommended)

1) Fast iteration (recommended for development) ✅
- Start the frontend dev server (Vite) with HMR and the backend with reload:
  - `# in one terminal` cd app && npm run dev
  - `# in another` DB_TYPE=sqlite python -m uvicorn canon.app:app --reload --port 8001
- Alternatively use the VS Code Run view: select **Run Frontend + Backend (dev)** (compound config) to start both.

2) Production-like (serve built UI from backend) ✅
- Build the frontend and serve it from FastAPI (useful for smoke tests):
  - `cd app && npm run build`
  - `FRONTEND_STATIC_DIR="${PWD}/app/dist" DB_TYPE=sqlite python -m uvicorn canon.app:app --port 8001`
- VS Code: use **Launch Backend (serve built UI)** which runs the build task and sets `FRONTEND_STATIC_DIR` for you.

Notes:
- `FRONTEND_STATIC_DIR` controls where FastAPI serves static assets from (defaults to `static`).
- `CORS_ORIGINS` may be set (comma-separated) if you need to allow cross-origin requests in dev; the app does not enable localhost CORS by default.

Note: If you'd like, I can attempt to install `pyenv` and the requested Python version locally for you now — say “yes” and I will run the required commands (I will not make system changes without your explicit confirmation).