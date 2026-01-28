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

# Virtualenv usage (skill)

Purpose
- Ensure a project venv is present and used for all Python tooling.

Commands (recommended)
- Check for venv: `test -d .venv` (ask before creating)
- Install runtime deps: `.venv/bin/python -m pip install -r requirements.txt`
- Install dev deps: `.venv/bin/python -m pip install -r requirements.dev.txt`
- Run tools via venv interpreter: `.venv/bin/python -m <tool>`

Guidelines
- Prefer explicit `.venv/bin/python -m` invocations for reliability in CI and remote
  sessions.
- Only use `source .venv/bin/activate` when an interactive shell session is required.
- Do NOT clear `.mypy_cache` routinely; only clear if `mypy` fails and re-run.

Examples
- Correct: `.venv/bin/python -m mypy .`
- Acceptable: `source .venv/bin/activate && mypy .`

Safety
- Ask for confirmation before creating or modifying `.venv/`.
