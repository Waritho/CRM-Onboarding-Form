#!/bin/bash
# Render Deployment Script
# Note: We do NOT use 'set -e' globally so that non-critical failures
# (like Celery worker) don't prevent Uvicorn from starting.

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 1. Run Database Migrations (CRITICAL)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
echo "==> Running database migrations..."
alembic upgrade head
if [ $? -ne 0 ]; then
    echo "==> [ERROR] Alembic migration failed. Aborting."
    exit 1
fi
echo "==> Migrations complete."

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 2. Start Celery Worker (OPTIONAL â€” skipped if Redis URL not set or not reachable)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if [ -n "$CELERY_BROKER_URL" ] && [[ "$CELERY_BROKER_URL" != *"127.0.0.1"* ]]; then
    echo "==> Starting Celery worker in background..."
    celery -A app.celery_app worker --loglevel=info --concurrency=1 &
    CELERY_PID=$!
    echo "==> Celery worker started with PID $CELERY_PID"
else
    echo "==> [WARNING] CELERY_BROKER_URL is not set or points to localhost. Celery worker skipped."
    echo "==> Emails will be sent synchronously (fallback mode)."
fi

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 3. Start FastAPI with Uvicorn (ALWAYS runs)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
echo "==> Starting FastAPI app with Uvicorn on port ${PORT:-10000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}