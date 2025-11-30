# Backend Dockerfile: FastAPI + Gunicorn (Uvicorn workers)

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# System deps
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt \
    && pip install gunicorn uvicorn

# Copy backend source
COPY . /app

# Expose API port
EXPOSE 8000

# Default Gunicorn+Uvicorn command (can be overridden in docker-compose)
CMD [
  "gunicorn",
  "main:app",
  "-k", "uvicorn.workers.UvicornWorker",
  "--workers", "4",
  "--worker-class", "uvicorn.workers.UvicornWorker",
  "--bind", "0.0.0.0:8000",
  "--timeout", "60"
]
