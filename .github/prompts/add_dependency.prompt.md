# Add dependency (prompt template)

Task
- Add a runtime or dev dependency and update the relevant requirements file.

Template
- "Add `<package>` version `>=<version>` to `requirements.txt` (runtime) or
  `requirements.dev.txt` (dev/stub). Install it into `.venv` and run checks."

Response
- List the exact file edits and the install commands you'd run. Include
  any recommended stub packages (e.g., `types-...`).
