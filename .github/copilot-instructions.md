### Python Linting & Formatting Conventions

- All module-level imports **must** appear at the top of the file, before any code, docstrings, or function/class definitions (Ruff E402).
- All lines **must** be ≤88 characters unless an exception is explicitly justified (Ruff E501).
- Always use `raise ... from err` or `raise ... from None` in exception handlers to clarify error origins (Ruff B904).
- Remove unused imports and variables (Ruff F401, F841).
- Organize and sort imports using standard tools (Ruff I001, isort).
- Use double quotes for all string literals (Ruff Q000).
- Do not use `print` statements in production code (Ruff T201).
- Abstract base classes must have at least one `@abstractmethod` (Ruff B024).
- All code and tests must pass `ruff check .` and `mypy .` with zero errors or justified ignores.

**Copilot must:**
- Proactively fix or flag these issues in all new and modified code.
- Remind contributors to follow these conventions in PRs and code reviews.
# Copilot Instructions (Canonical)

**Purpose**: This file is the canonical source of truth for how the Copilot assistant should behave and interact with contributors in this repository. Keep this file up to date; avoid duplicating guidance in other files.

## Canonical & DRY rule ✅
- **Canonical location**: `.github/copilot-instructions.md` is the authoritative Copilot instruction document.
- **DRY principle**: Keep instructions and style decisions DRY. Prefer referencing documentation (`docs/Style.md`, `docs/Architecture.md`, `README.md`) and using code-level inheritance/reuse to avoid duplication and confusion.
- **No duplicates**: Do not create or maintain duplicate instruction documents. If you find similar content in other files, propose consolidation into this canonical file and remove the duplicates.
- **No autonomous repo changes**: Copilot MUST NOT create branches, commit, push, open PRs/issues, merge PRs, tag releases, or otherwise modify repository state without explicit, itemized, and recorded confirmation from the user. See "Git operations policy" below.

## High-level workflow
1. Confirm problem statement / goal with the user before designing a solution.
2. Propose an implementation plan and wait for explicit user confirmation before coding.
3. Propose a testing and verification plan; wait for user confirmation before executing tests or implementing changes.
4. Create a new branch using the agreed naming convention (e.g. `dev-...`, `feat-...`) and announce the branch name.
5. Iterate on implementation until the verification plan passes.
6. Ask the user to confirm completion of the work.
7. Update relevant project documentation (see `docs/Architecture.md`, `docs/Style.md`, and `README.md`).
8. Prompt the user to confirm committing changes to the branch.
9. After user confirms commit, prompt to open a PR (target: `dev`). Wait for user confirmation to open the PR.

> **Git operations policy — explicit confirmation required**: Copilot MUST NOT perform any repository-changing operation (create branches, make commits, push to remotes, open PRs or issues, merge, tag releases, or run destructive git commands) without explicit, itemized confirmation from a human. Before any such operation, Copilot must:
> - Clearly list the exact actions, affected files, target branch, branch name, and proposed commit message(s).
> - Show the exact git (and shell) commands it proposes to run and wait for the user to confirm them in text.
> - Ask whether the user prefers the assistant to run the commands or to have the user run them locally, and obtain explicit consent either way.
> - If asked to run commands, reconfirm the branch name and commit message and get final approval before executing.
>
> Copilot may prepare branch names, commit messages, PR titles and bodies, and CI workflow changes as drafts and present them for review, but must never execute or push them without the user's clear consent.

## Branching & commit conventions
- Branch name: `dev-<short-desc>` for iterative work; `feat/<short-desc>` or `feat-<short-desc>` for new features; `fix/<short-desc>` for fixes.
- Use Conventional Commits style (e.g., `feat: add payments model`, `fix: handle edge-case in auth`).
- Include a short, one-line summary and an optional body describing intent and testing notes.

## PR checklist (include in PR description)
- [ ] Problem statement confirmed by user
- [ ] Implementation plan approved by user
- [ ] Tests added / updated
- [ ] Verification steps documented and passing
- [ ] `docs/Architecture.md` updated (if architecture changed)
- [ ] `docs/Style.md` updated (if style choice changed)
- [ ] README updated (if user-visible behavior changed)

## Automation & enforcement
- Copilot should remind the user to update `docs/Architecture.md` and `docs/Style.md` when appropriate.
- Consider adding a CI check that verifies the canonical docs were updated when affected files change.

**Linter & formatting rules**
- **Do not** add ignores or disable checks in linter/formatter config files (e.g., `pyproject.toml`, `.ruff.toml`, `.flake8`) without a written justification that includes: the rule being ignored, the rationale, the risk assessment, and a link to a tracking issue or PR.
- Any change that weakens linting rules must be documented in the PR description and discussed with at least one reviewer.

**Auto-fix & repo checks**
- Before applying automatic fixes (e.g., `ruff --fix`, `isort`, `black`, or codemods), Copilot MUST present the findings, list the exact commands it plans to run, and ask the repository maintainer to confirm the action.
- If fixes are applied automatically, any changes that relax or ignore checks must include inline justification comments (e.g., `# type: ignore[code]  # reason: <explanation>` for mypy) and an explanation in `pyproject.toml` or a linked issue/PR.
- Additions to linter ignores should be accompanied by a short note in `pyproject.toml` describing why the ignore is necessary and how/when it can be removed.

**Virtual environment usage**
- **Always** use the project's virtual environment when installing packages, running tests, linters, or any commands that require Python packages. When a `.venv/` directory exists at the repository root, Copilot MUST either:
  - activate it: `source .venv/bin/activate` (or the platform equivalent), or
  - run commands via the venv Python: `.venv/bin/python -m pip install ...`, `.venv/bin/python -m pytest`, etc.
- When the assistant needs to install packages or modify the environment it must:
  1. Check for the presence of a `.venv/` at the repo root and report the finding.
  2. Present the exact shell commands it intends to run and ask the repository maintainer to confirm them in text before execution.
  3. Never install packages into the system Python or global site-packages without explicit approval.
- This rule applies to automated fixes, test runs, and any ad-hoc package install or environment change initiated by Copilot or via the scripts it runs.
## Instruction updates & proactive prompts
- When Copilot discovers missing, ambiguous, or useful guidance that should be added to this file (or related canonical docs), it should proactively prompt the user with:
  - A short explanation of what should be added and why.
  - A suggested change (diff, paragraph, or bullet points).
  - A question asking whether the user would like Copilot to prepare the edit as a draft (PR) or just record the suggestion for later.
- Copilot must not directly edit the canonical instructions or push the change without explicit user approval and an itemized confirmation that includes the target branch name and commit message.

---

This file is intentionally concise and prescriptive; for implementation details, testing patterns, or ADRs, please see `docs/` and relevant templates in `.github/`.
