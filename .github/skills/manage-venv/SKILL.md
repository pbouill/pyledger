---
name: "manage-venv"
id: "manage-venv"
description: "Create, activate, and manage the project virtualenv and dependencies."
triggers:
  - "manage venv"
  - "create venv"
  - "activate venv"
  - "use .venv"
prompt_templates:
  - name: "Create & install venv"
    file: "../prompts/venv_activation.prompt.md"
  - name: "Add runtime dependency"
    file: "../prompts/add_dependency.prompt.md"
---

# Manage venv (skill)

Purpose
- Create `.venv`, install `requirements.txt` and `requirements.dev.txt`, and provide utilities to inspect and upgrade packages.

Guidelines
- Prefer explicit invocations: use `.venv/bin/python -m <module>` in scripts/CI for determinism.
- Only use `source .venv/bin/activate` in interactive shells when needed.
- When `mypy` behaves inconsistently, use the clear cache helper: `.github/skills/run-checks/clear_mypy_cache.sh --check`.
- Use the `manage_venv.sh` script to create and maintain the venv rather than ad-hoc commands.

Scripts
- `manage_venv.sh --create` — create `.venv` and upgrade pip
- `manage_venv.sh --install` — install runtime and dev dependencies into `.venv`
- `manage_venv.sh --outdated` — list outdated packages in `.venv`
- `manage_venv.sh --upgrade` — upgrade outdated packages

Quick usage
- Create and install: `./.github/skills/manage-venv/manage_venv.sh --create && ./.github/skills/manage-venv/manage_venv.sh --install`
- Activate (interactive): `source .venv/bin/activate` or run explicit commands: `.venv/bin/python -m pytest -q`

Dependency management
Rules
- Add runtime packages to `requirements.txt` with `>=<version>` (e.g., `Django>=4.2`).
- Add type stubs and dev packages to `requirements.dev.txt` with `>=<version>`.

Checklist when adding a package
1. Add runtime package to `requirements.txt` (or `requirements.dev.txt` for dev-only).
2. If package needs stubs, add `types-<package>` to `requirements.dev.txt` (or let `typecheck.sh` suggest candidates).
3. Run `./.github/skills/manage-venv/manage_venv.sh --install` (or `.venv/bin/python -m pip install -r requirements.dev.txt && .venv/bin/python -m pip install -r requirements.txt`).
4. Run the canonical checks: `./.github/skills/run-checks/run_checks.sh` (or `./run_checks.sh --no-fix` in CI).

Notes
- Keep `requirements.txt` and `requirements.dev.txt` in sync with installed packages; prefer pinning to `>=` for reproducibility.
- If you use `mypy`'s `--install-types`, consider also adding the installed stubs to `requirements.dev.txt` so CI remains deterministic.
- CI jobs should use `.venv/bin/python -m pip install -r requirements.dev.txt` or call the `run-checks` skill scripts for consistency.
- This SKILL supersedes the former `venv-usage` skill (the `venv-usage` SKILL was merged and its directory removed).
