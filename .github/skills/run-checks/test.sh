#!/usr/bin/env bash
set -euo pipefail

# Run tests (pytest). Usage: test.sh
if [ ! -x ".venv/bin/python" ]; then
  echo "Virtualenv Python not found at .venv/bin/python. Create venv first."
  exit 1
fi
PY=.venv/bin/python

echo "Running pytest -q"
"$PY" -m pytest -q
