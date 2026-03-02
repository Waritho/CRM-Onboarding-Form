"""
ZeptoMail Email Sender Utility
Sends transactional emails using the ZeptoMail REST API.
"""

import requests
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# No longer hardcoding URL here, we'll use settings.ZEPTOMAIL_API_URL


def send_otp_email(to_email: str, otp_code: str) -> bool:
    """
    Send an OTP email to the given email address using ZeptoMail API.

    Args:
        to_email: The recipient's email address
        otp_code: The 6-digit OTP code

    Returns:
        True if email was sent successfully, False otherwise
    """

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": settings.ZEPTOMAIL_API_TOKEN,
    }

    payload = {
        "from": {
            "address": settings.ZEPTOMAIL_FROM_EMAIL,
            "name": settings.ZEPTOMAIL_FROM_NAME,
        },
        "to": [
            {
                "email_address": {
                    "address": to_email,
                }
            }
        ],
        "subject": "Your OTP Code - CRM Onboarding",
        "htmlbody": f"""
            <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 32px;">
                <h2 style="color: #2d3748; margin-bottom: 16px;">Your OTP Code</h2>
                <p style="color: #4a5568; font-size: 16px;">
                    Use the following OTP to complete your sign-in:
                </p>
                <div style="background: #f7fafc; border: 2px solid #e2e8f0; border-radius: 8px;
                            padding: 20px; text-align: center; margin: 24px 0;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #2b6cb0;">
                        {otp_code}
                    </span>
                </div>
                <p style="color: #718096; font-size: 14px;">
                    This OTP is valid for <strong>{settings.OTP_EXPIRY_MINUTES} minutes</strong>.
                    Do not share this code with anyone.
                </p>
                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">
                <p style="color: #a0aec0; font-size: 12px;">
                    If you did not request this OTP, please ignore this email.
                </p>
            </div>
        """,
        "track_clicks": True,
        "track_opens": True,
        "client_reference": "crm_auth_otp",
    }

    try:
        response = requests.post(
            settings.ZEPTOMAIL_API_URL,
            json=payload,
            headers=headers,
            timeout=10,
        )

        if response.ok:  # Accepts 200, 201, 202 etc.
            logger.info(f"OTP email sent successfully to {to_email}")
            return True
        else:
            logger.error(
                f"ZeptoMail API error: {response.status_code} - {response.text}"
            )
            return False

    except requests.exceptions.Timeout:
        logger.error(f"ZeptoMail API timeout for {to_email}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"ZeptoMail API request failed: {str(e)}")
        return False
