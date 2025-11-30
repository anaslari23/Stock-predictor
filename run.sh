#!/usr/bin/env bash

# Helper script to run Gunicorn with Uvicorn workers in production
# Usage: ./run.sh

set -euo pipefail

WORKERS=${WORKERS:-4}
BIND_ADDR=${BIND_ADDR:-0.0.0.0:8000}
TIMEOUT=${TIMEOUT:-60}

exec gunicorn \
  main:app \
  -k uvicorn.workers.UvicornWorker \
  --workers "${WORKERS}" \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind "${BIND_ADDR}" \
  --timeout "${TIMEOUT}"
