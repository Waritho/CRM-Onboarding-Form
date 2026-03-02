"""
Celery Application Configuration
Initializes the Celery instance with Redis as the broker.
"""

from celery import Celery
from app.config import settings

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
