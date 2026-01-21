# Architecture

**Purpose**: Document high-level architecture decisions, diagrams, and change log for the project.

## Rules for architecture changes
- **Mandatory**: Any architecture decision or change MUST be recorded here (or in a linked ADR file under `docs/architecture/`) before merging.
- Record the *reason* for the change, trade-offs considered, and links to PRs / issues.

## ADR template (use for non-trivial decisions)
- Title: short and descriptive
- Date:
- Status: (Proposed | Accepted | Rejected | Deprecated)
- Context: what problem or constraint exists
- Decision: what we will do
- Consequences: pros / cons and migration notes
- Related PR / Issue:

## Frontend: Vue 3 + Vite

- **Choice**: Vue 3 + Vite for developer DX, fast rebuilds, and modern tooling.
- **Dev workflow**: In development we recommend running the Vite dev server locally (`vite`) for hot module replacement (HMR) and FastAPI separately (with CORS enabled or a proxy). This yields the fastest iteration loop.
- **Production options**:
  - **Single-container approach (recommended for small deployments / simplicity)**: Use a multi-stage Docker build that runs Vite to build static assets, then copies the built static files into the FastAPI image (e.g., into `static/` or a `dist/` directory) and serve them using FastAPI's static file support or via an internal ASGI static middleware. This results in a single container image that serves both the API and the built frontend assets.
  - **Multi-service approach (recommended for larger deployments)**: Build and serve frontend assets from a dedicated static server (Nginx) or CDN and run FastAPI in a separate container. This allows independent scaling and simpler CDN caching.

**Trade-offs (single container vs multi-service)**
- Single container: ✓ simpler deployment and one image to manage — ✗ less flexible scaling and larger image size.
- Multi-service: ✓ independent scaling and better caching via CDN/Nginx — ✗ more infra complexity.

## Backend: FastAPI + Postgres

- **Choice**: FastAPI for HTTP API and async support; SQLAlchemy for ORM; PostgreSQL as primary data store.
- **DB migrations**: Manage schema changes via Alembic.
- **Connection strategy**: Use connection pooling and environment-driven DB credentials (e.g., via secrets manager or env vars). For tests use a disposable test database (containerized or ephemeral).

## Deployment patterns
- Local dev: Run `uvicorn` (or use `pytest`/`tox` for tests) and Vite dev server separately for best DX.
- CI: Build frontend assets (Vite) and backend package, run unit tests and linters, and produce a multi-stage build image.
- Production: Use container orchestration (Kubernetes, docker-compose for small deploys) or single container (FastAPI serving built frontend) depending on scale.

## Architecture diagram

```mermaid
flowchart LR
  subgraph AppContainer[Application Container]
    direction TB
    API[FastAPI API server]
    Static[Built frontend assets (Vue/Vite)]
  end
  DB[(Postgres)]
  Client[Browser]
  CDN[/Optional CDN/]

  Client -->|HTTPS| CDN
  CDN -->|HTTPS| AppContainer
  Client -->|HTTPS| AppContainer
  AppContainer -->|TCP| DB
  AppContainer -->|serves static| Static
```

## Change log (example entries)
- 2026-01-21 — Initial project architecture: FastAPI + SQLAlchemy + Postgres backend; Vue 3 + Vite frontend. — @copilot

> Note: Copilot must update this file (or add an ADR in `docs/architecture/`) when proposing or applying an architecture change.