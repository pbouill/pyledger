#!/usr/bin/env bash
set -euo pipefail

# Simple detector for mypy internal errors vs normal type errors.
# Returns 0 if the file contains evidence of an internal mypy failure
# (traceback, KeyError/AttributeError in mypy internals), else returns 1.

if [ $# -ne 1 ]; then
  echo "Usage: $0 <mypy_output_file>" >&2
  exit 2
fi

OUT_FILE="$1"
if [ ! -f "$OUT_FILE" ]; then
  echo "File not found: $OUT_FILE" >&2
  exit 2
fi

# Patterns indicating internal mypy failure
if grep -E "Traceback \(most recent call last\)|KeyError: 'setter_type'|KeyError:|Internal error|AttributeError:|AssertionError:|mypy\\.__main__" "$OUT_FILE" >/dev/null 2>&1; then
  exit 0
fi

exit 1
