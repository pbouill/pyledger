#!/usr/bin/env bash
set -euo pipefail

# Backwards-compatible wrapper to the canonical skill version.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_SCRIPT="$SCRIPT_DIR/.github/skills/run-checks/clear_mypy_cache.sh"

if [ ! -x "$SKILL_SCRIPT" ]; then
  echo "Skill script not found or not executable: $SKILL_SCRIPT"
  exit 1
fi

exec "$SKILL_SCRIPT" "$@"
