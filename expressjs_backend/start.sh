#!/usr/bin/env bash
set -euo pipefail

# Start FastAPI using the project's venv if present.
#
# Many preview runners call a generic "python/uvicorn" without activating the venv,
# which leads to ModuleNotFoundError (fastapi/motor/etc.) and manifests as 502.
#
# This script also supports common platform env vars:
# - PORT / HOST
# - UVICORN_PORT / UVICORN_HOST / UVICORN_WORKERS
#
# Usage:
#   ./start.sh

HOST="${UVICORN_HOST:-${HOST:-0.0.0.0}}"
PORT="${UVICORN_PORT:-${PORT:-3010}}"
WORKERS="${UVICORN_WORKERS:-1}"

if [[ -x "./venv/bin/uvicorn" ]]; then
  exec ./venv/bin/uvicorn src.api.main:app --host "${HOST}" --port "${PORT}" --workers "${WORKERS}"
fi

# Fallback: try running uvicorn via the current interpreter.
exec python -m uvicorn src.api.main:app --host "${HOST}" --port "${PORT}" --workers "${WORKERS}"
