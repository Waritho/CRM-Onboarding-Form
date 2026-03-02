"""
Celery Application Configuration
Initializes the Celery instance with Redis as the broker.

NOTE: Initialization is wrapped in try/except so that if Redis is
unavailable (e.g. on Render free tier), the FastAPI app still starts.
Email sending will fall back to synchronous mode in auth_service.
"""

import logging
from app.config import settings

logger = logging.getLogger(__name__)

celery_app = None  # Will be None if Redis is not available

try:
    from celery import Celery

    celery_app = Celery(
        "crm_onboarding",
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND,
    )

    # Configuration
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="Asia/Kolkata",
        enable_utc=True,

        # Retry config for failed tasks
        task_acks_late=True,
        task_reject_on_worker_lost=True,

        # Auto-discover tasks in the 'app.tasks' module
        imports=["app.tasks.email_tasks"],
    )

    logger.info("Celery app initialized successfully with Redis broker.")

except Exception as e:
    logger.warning(f"Celery initialization failed: {e}. Email will be sent synchronously.")
