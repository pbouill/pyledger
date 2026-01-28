---
name: "git-and-confirmation"
id: "git-and-confirmation"
description: "Explicit confirmation policy and git command templates for Copilot."
triggers:
  - "create branch"
  - "commit changes"
prompt_templates:
  - name: "Git confirmation"
    file: "../prompts/git_confirm.prompt.md"
---

# Git & confirmation (skill)

Policy summary
- Copilot MUST NOT perform repo-changing operations without explicit, itemized
  confirmation from the user.

Confirmation checklist
- Branch name (suggested): `dev-<short-desc>` or `feat/<short-desc>`.
- Exact files to change and a short commit message.
- Exact git commands Copilot will run and whether to push/open a PR.

Example workflow
1. `git checkout -b dev/venv-instructions`
2. `git add .github/copilot-instructions.md .github/skills/*`
3. `git commit -m "docs: add venv and skills guidance"`
4. Ask user to confirm push and PR creation.
