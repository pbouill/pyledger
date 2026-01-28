---
name: "dependency-management"
id: "dependency-management"
description: "How to add runtime and type stub dependencies consistently."
triggers:
  - "add dependency"
  - "update requirements"
prompt_templates:
  - name: "Add runtime dependency"
    file: "../prompts/add_dependency.prompt.md"
---

# Dependency management (skill)

Rules
- Add runtime packages to `requirements.txt` with `>=<version>`.
- Add type stubs and dev packages to `requirements.dev.txt` with `>=<version>`.

Commands
- Install: `.venv/bin/python -m pip install -r requirements.txt` and
  `.venv/bin/python -m pip install -r requirements.dev.txt`.
- After adding a package, run `ruff`, `mypy`, and `pytest`.

Notes
- If a package lacks stubs, prefer adding `types-<package>` to
  `requirements.dev.txt`. Use `mypy --install-types` as a helpful alternative.
