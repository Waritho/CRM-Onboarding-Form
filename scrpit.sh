#!/bin/bash
set -e  # Exit immediately if a command exits with non-zero status

echo "Running database migrations..."
alembic upgrade head

echo "Starting FastAPI app..."
exec uvicorn main:app --host 0.0.0.0 --port 8000