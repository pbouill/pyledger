---
name: "compose-manager"
id: "compose-manager"
description: "Manage Docker Compose for local development (script + docs)."
triggers:
  - "manage compose"
---

# Compose Manager (skill)

Purpose
- Canonical location for the project's Docker Compose management scripts.
- Provide discoverable scripts to start, rebuild, or restart the compose stack.

Files
- `manage_compose.sh` — script to start, rebuild, or restart the compose stack.

Usage
- Start the stack: `./.github/skills/compose-manager/manage_compose.sh`
- Rebuild images: `./.github/skills/compose-manager/manage_compose.sh --rebuild`
- Restart containers (no volume removal): `./.github/skills/compose-manager/manage_compose.sh --restart`

Notes
- Best practices: skills should be placed under `.github/skills/` (see https://code.visualstudio.com/docs/copilot/customization/agent-skills)
- `start_compose.sh` at repo root is a thin wrapper to maintain backward compatibility; prefer calling the skill directly.
