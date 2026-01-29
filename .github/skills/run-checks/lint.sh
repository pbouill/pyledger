#!/usr/bin/env bash
set -euo pipefail

# Run linting step (ruff). Usage: lint.sh [--no-fix]
FIX=true
for arg in "$@"; do
  case "$arg" in
    --no-fix)
      FIX=false
      ;;
    -h|--help)
      echo "Usage: $0 [--no-fix]"
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg"
      echo "Usage: $0 [--no-fix]"
      exit 1
      ;;
  esac
done

if [ ! -x ".venv/bin/python" ]; then
  echo "Virtualenv Python not found at .venv/bin/python. Create venv first."
  exit 1
fi
PY=.venv/bin/python
if [ "$FIX" = true ]; then
  echo "Running ruff --fix ."
  "$PY" -m ruff check . --fix
else
  echo "Running ruff check ."
  "$PY" -m ruff check .
fi
