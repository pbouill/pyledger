## Internationalization and Validation

This project uses [pycountry](https://pypi.org/project/pycountry/) for ISO 3166-1 country codes, ISO 639 language codes, and ISO 4217 currency codes. All country, language, and currency fields in models are validated using pycountry to ensure correctness and up-to-date standards.
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


Note: If you'd like, I can attempt to install `pyenv` and the requested Python version locally for you now — say “yes” and I will run the required commands (I will not make system changes without your explicit confirmation).