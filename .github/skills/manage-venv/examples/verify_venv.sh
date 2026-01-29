#!/usr/bin/env bash
set -euo pipefail

# Simple smoke script: create venv, install dev deps, run ruff quickly
if [ ! -x ".venv/bin/python" ]; then
  echo "Creating .venv..."
  python -m venv .venv
fi
.venv/bin/python -m pip install --upgrade pip
if [ -f requirements.dev.txt ]; then
  .venv/bin/python -m pip install -r requirements.dev.txt
fi
.venv/bin/python -m ruff check . --fix --quiet || true
echo "venv verified"
