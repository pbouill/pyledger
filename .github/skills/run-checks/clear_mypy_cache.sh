#!/usr/bin/env bash
set -euo pipefail

# Mypy cache cleanup (canonical skill copy in .github location)
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)")
mapfile -t CACHES < <(find "$REPO_ROOT" -type d -name ".mypy_cache" -print 2>/dev/null)
if [ "${#CACHES[@]}" -eq 0 ]; then
  echo "No .mypy_cache directories found under $REPO_ROOT"
else
  echo "Removing ${#CACHES[@]} .mypy_cache directories..."
  for d in "${CACHES[@]}"; do
    echo "Removing $d"
    rm -rf "$d"
  done
  echo "Removal complete."
fi

if [ "${1-}" = "--check" ]; then
  if [ -x ".venv/bin/python" ]; then
    echo "Running mypy via .venv/bin/python -m mypy ."
    .venv/bin/python -m mypy .
  else
    echo "Warning: .venv/bin/python not found. Run mypy manually or activate a venv."
    exit 1
  fi
fi
