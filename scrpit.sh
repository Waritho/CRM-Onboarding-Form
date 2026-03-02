#!/bin/bash
set -e

# 1. Run Migrations
echo "==> Running database migrations..."
alembic upgrade head

# 2. Start Celery Worker in the background
if [ -n "$CELERY_BROKER_URL" ]; then
    echo "==> Starting Celery worker..."
    celery -A app.celery_app worker --loglevel=info --concurrency=1 &
else
    echo "==> [WARNING] CELERY_BROKER_URL not set. Celery worker skipped."
fi

# 3. Start FastAPI with Uvicorn
echo "==> Starting FastAPI app with Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}