# Activate project venv and run checks

Task
- Ensure `.venv` exists and is used; if missing, ask user before creating.

Steps
1. Check for `.venv`: `test -d .venv` (or ask user).
2. Install runtime and dev packages:
   - `.venv/bin/python -m pip install -r requirements.txt`
   - `.venv/bin/python -m pip install -r requirements.dev.txt`
3. Run checks:
   - `.venv/bin/python -m ruff check .`
   - `.venv/bin/python -m mypy .`
   - `.venv/bin/python -m pytest -q`

Response format
- Provide the command executed and a single-line summary of the result.
- If any step failed, include error output and suggested next steps.
