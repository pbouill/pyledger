# Multi-stage Dockerfile for pyledger
# - Builds frontend (Vue + Vite) in a Node stage
# - Installs Python dependencies and copies app code in a builder stage
# - Produces a small runtime image which serves the API and built static assets
#
# Usage notes:
# - Set the Python version and tag suffix for this build with build-args, e.g.:
#   docker build --build-arg PYTHON_VERSION="$(cat .python-version)" --build-arg PYTHON_TAG_SUFFIX="-slim" -t pyledger .
# - Alternatively export PYTHON_VERSION and PYTHON_TAG_SUFFIX in your environment or use docker-compose build which can pass build args.

ARG PYTHON_VERSION=3.14.2
ARG PYTHON_TAG_SUFFIX=-slim
ARG NODE_VERSION=24
ARG NODE_TAG_SUFFIX=-alpine
ARG FRONTEND_DIR=frontend

#################################################################
# Frontend build stage
#################################################################
FROM node:${NODE_VERSION}${NODE_TAG_SUFFIX} AS frontend-build
WORKDIR /build-frontend

# Copy only package files first for better caching
COPY ${FRONTEND_DIR}/package*.json ./
# If you use yarn, change commands accordingly
RUN npm ci --silent

# Copy the rest of the frontend sources and build
COPY ${FRONTEND_DIR}/ ./
RUN npm run build

#################################################################
# Python builder stage
#################################################################
FROM python:${PYTHON_VERSION}${PYTHON_TAG_SUFFIX} AS builder
WORKDIR /app

# Install OS packages required for building some Python packages (e.g., psycopg2)
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential libpq-dev gcc \
  && rm -rf /var/lib/apt/lists/*

# Install Python dependencies and build wheels for reliable transfer to runtime image
COPY requirements.txt ./
RUN python -m pip install --upgrade pip
RUN pip wheel --wheel-dir=/wheels -r requirements.txt

# Copy application source
COPY . .

# (Optional) run tests / packaging here in CI builds

#################################################################
# Final runtime image
#################################################################
FROM python:${PYTHON_VERSION}${PYTHON_TAG_SUFFIX} AS runtime
WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Create a non-root user to run the app
RUN useradd --create-home --shell /bin/bash appuser || true

# Copy wheels from the builder stage and install (no network needed)
COPY --from=builder /wheels /wheels
RUN python -m pip install --no-index --no-cache-dir /wheels/* || true

# Copy application code and built frontend assets
COPY --from=builder /app /app
COPY --from=frontend-build /build-frontend/dist /app/static

# Adjust permissions
RUN chown -R appuser:appuser /app

USER appuser
EXPOSE 8000

# Healthcheck to verify the app is responding on the expected endpoint
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=5 \
  CMD ["python", "-c", "import sys,urllib.request as r; v=r.urlopen('http://127.0.0.1:8000/health', timeout=5); sys.exit(0 if v.getcode()<400 else 1)"]

# Default command: run uvicorn (override in production with your process manager if desired)
CMD ["uvicorn", "pyledger.main:app", "--host", "0.0.0.0", "--port", "8000"]
