#!/bin/bash
set -e

echo "Running database migrations..."
alembic -c alembic.ini upgrade head

echo "Starting FastAPI app..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT