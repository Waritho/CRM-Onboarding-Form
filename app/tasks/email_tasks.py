"""
Celery Tasks for Email Sending
These functions run in the Celery worker process, NOT in the FastAPI process.

If Celery is not available (no Redis), fall back to synchronous email sending.
"""

import logging
from app.celery_app import celery_app
from app.utils.email_sender import send_otp_email

logger = logging.getLogger(__name__)


def send_otp_email_task_sync(to_email: str, otp_code: str):
    """
    Synchronous fallback: Send OTP email directly (no Celery).
    Used when Redis/Celery is not available (e.g. on Render free tier).
    """
    try:
        success = send_otp_email(to_email=to_email, otp_code=otp_code)
        if success:
            logger.info(f"[Sync] OTP email sent to {to_email}")
        else:
            logger.error(f"[Sync] Failed to send OTP email to {to_email}")
    except Exception as e:
        logger.error(f"[Sync] Error sending OTP email to {to_email}: {e}")


# Only define the Celery task if Celery is available
if celery_app is not None:
    @celery_app.task(
        bind=True,
        max_retries=3,
        default_retry_delay=60,
        name="send_otp_email_task",
    )
    def send_otp_email_task(self, to_email: str, otp_code: str):
        """
        Celery task: Send OTP email in the background.
        """
        try:
            success = send_otp_email(to_email=to_email, otp_code=otp_code)

            if success:
                logger.info(f"[Celery] OTP email sent to {to_email}")
                return {"status": "sent", "email": to_email}
            else:
                logger.error(f"[Celery] Permanent API failure for {to_email}. Will NOT retry.")
                return {"status": "failed", "email": to_email}

        except Exception as exc:
            logger.error(f"[Celery] Network/system error for {to_email}: {str(exc)}. Retrying...")
            raise self.retry(exc=exc)
else:
    # If Celery is not available, create a dummy that just calls sync
    send_otp_email_task = None
