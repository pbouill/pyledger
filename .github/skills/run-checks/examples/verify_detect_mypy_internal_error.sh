#!/usr/bin/env bash
set -euo pipefail

# Smoke verifier for detect_mypy_internal_error.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DETECT="$SCRIPT_DIR/detect_mypy_internal_error.sh"

echo "Running detector smoke checks..."

echo "Checking internal traceback example..."
printf "Traceback (most recent call last):\n  File \"mypy/main.py\", line 1\nKeyError: 'setter_type'\n" > /tmp/_mypy_sample_1.txt
if "$DETECT" /tmp/_mypy_sample_1.txt; then
  echo "OK: detector matched traceback sample"
else
  echo "FAIL: detector did not match traceback sample" >&2
  exit 1
fi

echo "Checking internal message example..."
echo "Internal error: something bad" > /tmp/_mypy_sample_2.txt
if "$DETECT" /tmp/_mypy_sample_2.txt; then
  echo "OK: detector matched internal message sample"
else
  echo "FAIL: detector did not match internal message sample" >&2
  exit 1
fi

echo "Checking normal mypy output sample (should NOT match)..."
echo "tests/foo.py:10: error: Incompatible types" > /tmp/_mypy_sample_3.txt
if "$DETECT" /tmp/_mypy_sample_3.txt; then
  echo "FAIL: detector incorrectly matched normal mypy output" >&2
  exit 1
else
  echo "OK: detector ignored normal mypy output"
fi

rm -f /tmp/_mypy_sample_1.txt /tmp/_mypy_sample_2.txt /tmp/_mypy_sample_3.txt

echo "All smoke checks passed."