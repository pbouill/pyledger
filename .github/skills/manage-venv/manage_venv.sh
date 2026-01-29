#!/usr/bin/env bash
set -euo pipefail

# Manage project virtualenv and install dependencies
# Usage:
#  ./manage_venv.sh --create   # create .venv if missing
#  ./manage_venv.sh --install  # install requirements into .venv
#  ./manage_venv.sh --outdated # list outdated packages in .venv
#  ./manage_venv.sh --upgrade  # upgrade outdated packages interactively

ACTION=""
for arg in "$@"; do
  case "$arg" in
    --create)
      ACTION="create"
      ;;
    --install)
      ACTION="install"
      ;;
    --outdated)
      ACTION="outdated"
      ;;
    --upgrade)
      ACTION="upgrade"
      ;;
    -h|--help)
      echo "Usage: $0 [--create|--install|--outdated|--upgrade]"
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg"
      exit 1
      ;;
  esac
done

if [ -z "$ACTION" ]; then
  echo "No action specified. Use --help for options."
  exit 1
fi

if [ "$ACTION" = "create" ]; then
  if [ -d ".venv" ]; then
    echo ".venv already exists."
  else
    python -m venv .venv
    .venv/bin/python -m pip install --upgrade pip
    echo ".venv created and pip upgraded."
  fi
  exit 0
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "Virtualenv not found. Create it with --create"
  exit 1
fi
PY=.venv/bin/python

if [ "$ACTION" = "install" ]; then
  echo "Installing runtime dependencies from requirements.txt"
  if [ -f requirements.txt ]; then
    "$PY" -m pip install -r requirements.txt
  fi
  echo "Installing dev dependencies from requirements.dev.txt"
  if [ -f requirements.dev.txt ]; then
    "$PY" -m pip install -r requirements.dev.txt
  fi
  exit 0
fi

if [ "$ACTION" = "outdated" ]; then
  echo "Listing outdated packages in .venv"
  "$PY" -m pip list --outdated
  exit 0
fi

if [ "$ACTION" = "upgrade" ]; then
  echo "Upgrading outdated packages interactively"
  mapfile -t OUT < <("$PY" -m pip list --outdated --format=freeze | sed -E 's/=.*//')
  for p in "${OUT[@]}"; do
    echo "Upgrading $p"
    "$PY" -m pip install -U "$p"
  done
  exit 0
fi
