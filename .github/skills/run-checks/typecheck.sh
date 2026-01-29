#!/usr/bin/env bash
set -euo pipefail

# Run type checking (mypy). Usage: typecheck.sh [--clear-on-failure]
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLEAR_ON_FAILURE=false
FORCE_CLEAR=false
for arg in "$@"; do
  case "$arg" in
    --clear-on-failure)
      CLEAR_ON_FAILURE=true
      ;;
    --force-clear)
      FORCE_CLEAR=true
      ;;
    -h|--help)
      echo "Usage: $0 [--clear-on-failure] [--force-clear]"
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg"
      echo "Usage: $0 [--clear-on-failure] [--force-clear]"
      exit 1
      ;;
  esac
done

if [ ! -x ".venv/bin/python" ]; then
  echo "Virtualenv Python not found at .venv/bin/python. Create venv first."
  exit 1
fi
PY=.venv/bin/python

echo "Running mypy ."
TMP_OUTPUT="$(mktemp)"
if "$PY" -m mypy . 2>&1 | tee "$TMP_OUTPUT"; then
  rm -f "$TMP_OUTPUT"
  exit 0
else
  echo "mypy failed. Inspecting errors..."
  # Only attempt automatic cache clearing when an internal mypy failure is
  # detected (e.g., KeyError in mypy internals), or when user explicitly
  # requests `--force-clear`.
  if [ "$CLEAR_ON_FAILURE" = true ] || [ "$FORCE_CLEAR" = true ]; then
    if "$SCRIPT_DIR/detect_mypy_internal_error.sh" "$TMP_OUTPUT"; then
      echo "Detected mypy internal error."
      echo "Attempting to clear mypy cache and re-run mypy (this will also run mypy):"
      if "$SCRIPT_DIR/clear_mypy_cache.sh" --check; then
        echo "mypy passed after clearing cache"
        rm -f "$TMP_OUTPUT"
        exit 0
      else
        echo "Clearing cache did not fix internal mypy error"
      fi
    else
      if [ "$FORCE_CLEAR" = true ]; then
        echo "--force-clear provided: attempting to clear mypy cache despite no internal error detected."
        if "$SCRIPT_DIR/clear_mypy_cache.sh" --check; then
          echo "mypy passed after clearing cache"
          rm -f "$TMP_OUTPUT"
          exit 0
        else
          echo "Clearing cache did not resolve mypy failures."
        fi
      else
        echo "mypy reported regular type errors. Not clearing cache automatically."
        echo "To attempt automatic cache clearing for internal mypy errors, re-run with --clear-on-failure."
        echo "To force a cache clear attempt, run with --force-clear."
        echo "See $TMP_OUTPUT for details."
        exit 1
      fi
    fi
  fi

  # Detect missing stubs or modules
  MISSING_PKGS=()
  if grep -E "Library stubs not installed for package\(s\):" "$TMP_OUTPUT" >/dev/null 2>&1; then
    LIST=$(grep -E "Library stubs not installed for package\(s\):" "$TMP_OUTPUT" | sed -E "s/.*:\s*//")
    # split by comma
    IFS=',' read -ra ARR <<< "$LIST"
    for a in "${ARR[@]}"; do
      pkg=$(echo "$a" | tr -d ' ')
      MISSING_PKGS+=("$pkg")
    done
  fi
  # Also detect "Cannot find implementation or library stub for module named 'X'"
  while IFS= read -r line; do
    if echo "$line" | grep -q "Cannot find implementation or library stub for module named"; then
      mod=$(echo "$line" | sed -E "s/.*named '([^']+)'.*/\1/")
      MISSING_PKGS+=("$mod")
    fi
  done < "$TMP_OUTPUT"

  if [ ${#MISSING_PKGS[@]} -gt 0 ]; then
    echo "Detected missing stubs or modules: ${MISSING_PKGS[*]}"
    # Ensure requirements.dev.txt exists so we can append safely
    if [ ! -f requirements.dev.txt ]; then
      echo "requirements.dev.txt not found; creating an empty one"
      touch requirements.dev.txt
    fi
    for mod in "${MISSING_PKGS[@]}"; do
      types_pkg="types-$mod"
      # Skip if already listed
      if grep -qE "^${types_pkg}(|>=)" requirements.dev.txt 2>/dev/null; then
        echo "$types_pkg already present in requirements.dev.txt"
        continue
      fi
      echo "Attempting to install $types_pkg into .venv and add to requirements.dev.txt"
      if "$PY" -m pip install -U "$types_pkg"; then
        ver=$($PY -m pip show "$types_pkg" | awk '/Version:/{print $2}')
        if [ -n "$ver" ]; then
          echo "$types_pkg>=$ver" >> requirements.dev.txt
        else
          echo "$types_pkg" >> requirements.dev.txt
        fi
        echo "Added $types_pkg to requirements.dev.txt and installed into .venv"
      else
        echo "Could not install $types_pkg automatically; please add an appropriate types package to requirements.dev.txt"
      fi
    done

    echo "Re-running mypy after installing candidate stubs..."
    if "$PY" -m mypy .; then
      echo "mypy now passes after installing stubs"
      rm -f "$TMP_OUTPUT"
      exit 0
    fi
  fi

  echo "mypy still failing. See $TMP_OUTPUT for details."
  exit 1
fi
