#!/usr/bin/env bash
set -euo pipefail

# Run checks skill script
# Usage: ./run_checks.sh [--no-fix] [--mypy-only] [--clear-on-failure]
# - By default: run `ruff --fix`, `mypy`, and `pytest` using the project's .venv

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -x ".venv/bin/python" ]; then
  echo "Virtualenv not found at .venv. You can create it with:"
  echo "  python -m venv .venv && .venv/bin/python -m pip install -r requirements.dev.txt"
  echo "Or use the manage-venv skill: .github/skills/manage-venv/manage_venv.sh --create --install"
  exit 1
fi

NO_FIX=false
MYPY_ONLY=false
CLEAR_ON_FAILURE=false
for arg in "$@"; do
  case "$arg" in
    --no-fix)
      NO_FIX=true
      ;;
    --mypy-only)
      MYPY_ONLY=true
      ;;
    --clear-on-failure)
      CLEAR_ON_FAILURE=true
      ;;
    -h|--help)
      echo "Usage: $0 [--no-fix] [--mypy-only] [--clear-on-failure]"
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg"
      echo "Usage: $0 [--no-fix] [--mypy-only] [--clear-on-failure]"
      exit 1
      ;;
  esac
done

if [ "$MYPY_ONLY" = true ]; then
  exec "$SCRIPT_DIR/typecheck.sh" $( [ "$CLEAR_ON_FAILURE" = true ] && echo "--clear-on-failure" )
fi

if [ "$NO_FIX" = true ]; then
  "$SCRIPT_DIR/lint.sh" --no-fix
else
  "$SCRIPT_DIR/lint.sh"
fi

# Run typecheck and tests; typecheck.sh can optionally auto-clear cache on failure
"$SCRIPT_DIR/typecheck.sh" $( [ "$CLEAR_ON_FAILURE" = true ] && echo "--clear-on-failure" )

"$SCRIPT_DIR/test.sh"

