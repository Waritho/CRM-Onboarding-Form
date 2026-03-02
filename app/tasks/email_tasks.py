"""
Celery Tasks for Email Sending
These functions run in the Celery worker process, NOT in the FastAPI process.
"""

import logging
from app.celery_app import celery_app
from app.utils.email_sender import send_otp_email

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # Wait 60 seconds before retry
    name="send_otp_email_task",
)
def send_otp_email_task(self, to_email: str, otp_code: str):
    """
    Celery task: Send OTP email in the background.

    IMPORTANT: We only retry on NETWORK errors (timeout, connection refused).
    We do NOT retry on API errors (wrong key, bad domain) because those are
    permanent failures — retrying would just spam the user.
    """
    try:
        success = send_otp_email(to_email=to_email, otp_code=otp_code)

        if success:
            logger.info(f"[Celery] OTP email sent to {to_email}")
            return {"status": "sent", "email": to_email}
        else:
            # API returned an error (401, 403, 422, etc.)
            # Do NOT retry — this is a permanent failure
            logger.error(f"[Celery] Permanent API failure for {to_email}. Will NOT retry.")
            return {"status": "failed", "email": to_email}

    except Exception as exc:
        # Network error, timeout, connection refused, etc.
        # These ARE worth retrying
        logger.error(f"[Celery] Network/system error for {to_email}: {str(exc)}. Retrying...")
        raise self.retry(exc=exc)
