#!/usr/bin/env bash
set -euo pipefail

UVICORN_PID_FILE=".local/dev_local_uvicorn.pid"
FRONTEND_PID_FILE=".local/dev_local_frontend.pid"
KILLED=0

echo "[stop_dev] stopping dev processes..."

if [ -f "$UVICORN_PID_FILE" ]; then
  UVICORN_PID=$(cat "$UVICORN_PID_FILE" 2>/dev/null || true)
  if [ -n "$UVICORN_PID" ]; then
    if kill -0 "$UVICORN_PID" 2>/dev/null; then
      echo "[stop_dev] killing uvicorn pid $UVICORN_PID"
      kill "$UVICORN_PID" || true
      KILLED=1
    fi
  fi
  rm -f "$UVICORN_PID_FILE"
else
  echo "[stop_dev] uvicorn pidfile not found, attempting pattern kill"
  pkill -f "uvicorn canon.app:app" || true
fi

if [ -f "$FRONTEND_PID_FILE" ]; then
  FRONTEND_PID=$(cat "$FRONTEND_PID_FILE" 2>/dev/null || true)
  if [ -n "$FRONTEND_PID" ]; then
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
      echo "[stop_dev] killing frontend pid $FRONTEND_PID"
      kill "$FRONTEND_PID" || true
      KILLED=1
    fi
  fi
  rm -f "$FRONTEND_PID_FILE"
else
  # fallback to pattern kill for vite/node if pidfile not present
  ok=0
  pkill -f "vite" && ok=1 || true
  pkill -f "node .*vite" && ok=1 || true
  if [ "$ok" -eq 1 ]; then
    echo "[stop_dev] killed vite / frontend dev processes"
    KILLED=1
  fi
fi

if [ "$KILLED" -eq 0 ]; then
  echo "[stop_dev] no running dev processes found"
else
  echo "[stop_dev] done"
fi
