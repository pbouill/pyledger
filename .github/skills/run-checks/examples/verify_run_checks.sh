#!/usr/bin/env bash
set -euo pipefail

# Example smoke script that checks venv and shows commands that would be run.
if [ -x ".venv/bin/python" ]; then
  echo ".venv found. The run checks skill would run the following commands:"
  echo "  .venv/bin/python -m ruff check . --fix"
  echo "  .venv/bin/python -m mypy ."
  echo "  .venv/bin/python -m pytest -q"
else
  echo ".venv not found. Example output: create venv with 'python -m venv .venv' and install requirements.dev.txt"
fi
