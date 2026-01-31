#!/usr/bin/env bash
set -euo pipefail

# Lightweight local dev runner for rapid prototyping.
# Usage: ./scripts/dev_local.sh [--port PORT] [--db sqlite|postgres]


PORT=8001
DB_TYPE="sqlite"  # default to sqlite for rapid prototyping
BACKGROUND_ALL=0

# Ensure .local exists for runtime artifacts
mkdir -p .local
NO_FRONTEND=0
NO_BACKEND=0
BACKGROUND_FRONTEND=0
WATCH_BUILD=1  # default to build-watch for auto-building frontend changes
# Use --hmr to explicitly request Vite dev server (HMR) instead of build:watch

while [ "$#" -gt 0 ]; do
  case "$1" in
    --port)
      PORT="$2"
      shift 2
      ;;
    --db)
      DB_TYPE="$2"
      shift 2
      ;;
    --no-frontend)
      NO_FRONTEND=1
      shift
      ;;
    --no-backend)
      NO_BACKEND=1
      shift
      ;;
    --background-frontend)
      BACKGROUND_FRONTEND=1
      shift
      ;;
    --background|--detach|-d)
      BACKGROUND_ALL=1
      shift
      ;;
    --watch-build)
      WATCH_BUILD=1
      shift
      ;;
    --hmr)
      WATCH_BUILD=0
      shift
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

while [ "$#" -gt 0 ]; do
  case "$1" in
    --port)
      PORT="$2"
      shift 2
      ;;
    --db)
      DB_TYPE="$2"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

# Source local .env if present
if [ -f .env ]; then
  echo "[dev_local] loading .env"
  # shellcheck disable=SC1090
  . .env
fi

# Always serve built frontend from app/dist in dev unless overridden
if [ -z "${FRONTEND_STATIC_DIR:-}" ]; then
  export FRONTEND_STATIC_DIR="app/dist"
  echo "[dev_local] setting FRONTEND_STATIC_DIR=app/dist (default for dev)"
else
  echo "[dev_local] using FRONTEND_STATIC_DIR=$FRONTEND_STATIC_DIR"
fi

export DB_TYPE="$DB_TYPE"
# If using the postgres dev mode, point DB_HOST to localhost so we can talk to
# a compose-exposed DB on the host. This is safe when compose maps the DB to
# a host port (see compose.dev-override.yml). Otherwise the host should set
# DB_HOST/DB_PORT appropriately.
if [ "$DB_TYPE" = "postgres" ]; then
  export DB_HOST="${DB_HOST:-localhost}"
  export DB_PORT="${DB_PORT:-${DB_EXT_PORT:-5432}}"
fi

# If using compose DB, ensure host is accessible from host (compose dev-override maps DB_EXT_PORT)
# Always use .local/ as the DB directory for local dev DBs
DB_PATH=".local/"
export DB_PATH
# For local prototyping prefer sqlite (DB_TYPE=sqlite) since it needs no external DB.

cleanup() {
  echo "[dev_local] stopping uvicorn (pid $UVICORN_PID)"
  kill "$UVICORN_PID" 2>/dev/null || true
}

# The EXIT trap will be attached after uvicorn is started if the runner will
# stay alive (i.e., when not backgrounding the frontend). See below.

if [ "$NO_BACKEND" -eq 0 ]; then
  echo "[dev_local] starting backend on http://localhost:${PORT} (DB_TYPE=${DB_TYPE}, DB_PATH=${DB_PATH})"
  # Start backend in the background, redirecting stdout and stderr to .local/dev_local_backend.log
  .venv/bin/python -m uvicorn canon.app:app --reload --port "${PORT}" \
    > .local/dev_local_backend.log 2>&1 &
  UVICORN_PID=$!
  echo "$UVICORN_PID" > .local/dev_local_uvicorn.pid

  # If we are NOT backgrounding the frontend, the runner will remain alive in
  # the foreground and we should ensure uvicorn is cleaned up when the runner
  # exits. Only then attach the EXIT trap to stop uvicorn.
  if [ "${BACKGROUND_FRONTEND:-0}" -eq 0 ]; then
    trap cleanup EXIT
  fi

  # Wait for server to be up (simple loop)
  tries=0
  until curl -sSf "http://localhost:${PORT}/api/health" >/dev/null 2>&1 || [ "$tries" -ge 30 ]; do
    tries=$((tries+1))
    echo "[dev_local] waiting for backend to become ready ($tries/30)..."
    sleep 1
  done
  if [ "$tries" -ge 30 ]; then
    echo "[dev_local] warning: backend did not respond in time"
  fi
fi

if [ "$NO_FRONTEND" -eq 0 ]; then
  if [ "$BACKGROUND_ALL" -eq 1 ]; then
    # Background both backend and frontend, then exit
    if [ "$WATCH_BUILD" -eq 1 ]; then
      echo "[dev_local] starting frontend build-watch (background)"
      (cd app && npm run build:watch > ../.local/dev_local_frontend.log 2>&1) &
    else
      echo "[dev_local] starting frontend dev server (background)"
      (cd app && npm run dev > ../.local/dev_local_frontend.log 2>&1) &
    fi
    FRONTEND_PID=$!
    echo "$FRONTEND_PID" > .local/dev_local_frontend.pid
    echo "[dev_local] frontend background pid: $FRONTEND_PID"
    echo "[dev_local] dev runner exiting (backend + frontend running in background). Use ./scripts/stop_dev.sh to stop them."
    exit 0
  else
    if [ "$WATCH_BUILD" -eq 1 ]; then
      echo "[dev_local] starting frontend build-watch (foreground, logging to .local/dev_local_frontend.log)"
      cd app
      npm run build:watch > ../.local/dev_local_frontend.log 2>&1 &
      FRONTEND_PID=$!
      cd ..
    else
      echo "[dev_local] starting frontend dev server (foreground, logging to .local/dev_local_frontend.log)"
      cd app
      npm run dev > ../.local/dev_local_frontend.log 2>&1 &
      FRONTEND_PID=$!
      cd ..
    fi
    # Tail both backend and frontend logs until ctrl-c
    echo "[dev_local] Tailing backend and frontend logs. Press Ctrl-C to stop."
    tail -n 40 -F .local/dev_local_backend.log .local/dev_local_frontend.log
  fi
else
  echo "[dev_local] frontend disabled; sleeping until killed (backend running in background)"
  while true; do sleep 3600; done
fi
