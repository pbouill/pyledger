"""Project-level entrypoint to run the FastAPI backend.

We intentionally place this in the repo root per your preference. It imports
and runs `create_app` from the package-level `pyledger.app` (defined below).
"""
import uvicorn

from pyledger.app import create_app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")