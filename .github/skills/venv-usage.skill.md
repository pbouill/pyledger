---
name: "venv-usage"
id: "venv-usage"
description: "Rules and commands for using the project virtualenv in Copilot sessions."
triggers:
  - "activate venv"
  - "use .venv"
  - "run checks"
prompt_templates:
  - name: "Activate and run checks"
    file: "../prompts/venv_activation.prompt.md"
---

# DEPRECATED: This skill is replaced by `.github/skills/manage-venv/SKILL.md`.

(This file is deprecated; see `.github/skills/manage-venv/SKILL.md` for canonical venv usage and automation.)
