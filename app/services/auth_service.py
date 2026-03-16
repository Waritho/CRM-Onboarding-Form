from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import logging
from fastapi import HTTPException, status

from app.models.client import Client
from app.models.otp import OTP
from app.utils.otp_generator import generate_otp
from app.utils.jwt_handler import create_access_token, create_refresh_token
from app.config import settings
from app.tasks.email_tasks import send_otp_email_task, send_otp_email_task_sync
from app.models.client_user import ClientUser

logger = logging.getLogger(__name__)



# SEND OTP
def send_otp_service(email: str, db: Session):
    """
    Generates an OTP, saves it to the database, and dispatches 
    a background task to send the email.
    """
    
    # Get or create client
    client = db.query(Client).filter(Client.email == email).first()
    
    if client:
        client_id_for_otp = client.id
    else:
        sub_user = db.query(ClientUser).filter(
            ClientUser.email == email, 
            ClientUser.is_active == True
        ).first()
        if sub_user:
            client_id_for_otp = sub_user.client_id
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Email not registered. Please contact your administrator."
            )

    now = datetime.now(timezone.utc)

    # Check for existing valid OTP
    existing_otp = (
        db.query(OTP)
        .filter(
            OTP.client_id == client_id_for_otp,
            OTP.is_used.is_(False),
            OTP.expiry_at > now
        )
        .order_by(OTP.id.desc())
        .first()
    )

    if existing_otp:
        return {"message": "OTP already sent. Please check your email."}

    # Generate new OTP
    otp_code = generate_otp()
    expiry = now + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)

    otp_entry = OTP(
        client_id=client_id_for_otp,
        otp_code=otp_code,
        expiry_at=expiry,
        attempt_count=0,
        is_used=False
    )

    db.add(otp_entry)
    db.commit()

    # Send OTP via email (Celery if available, otherwise sync)
    if send_otp_email_task is not None:
        send_otp_email_task.delay(email, otp_code)
        logger.info(f"OTP email dispatched via Celery for {email}")
    else:
        send_otp_email_task_sync(email, otp_code)
        logger.info(f"OTP email sent synchronously for {email} (Celery unavailable)")

    return {"message": "OTP sent successfully"}


# VERIFY OTP (LOGIN)
def verify_otp_service(email: str, otp: str, db: Session):
    
    client = db.query(Client).filter(Client.email == email).first()
    role = "primary"
    
    if client:
        client_id_for_otp = client.id
    else:
        sub_user = db.query(ClientUser).filter(
            ClientUser.email == email, 
            ClientUser.is_active == True
        ).first()
        if sub_user:
            client_id_for_otp = sub_user.client_id
            role = "sub_user"
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid email")

    now = datetime.now(timezone.utc)

    # Get latest unused OTP
    otp_entry = (
        db.query(OTP)
        .filter(
            OTP.client_id == client_id_for_otp,
            OTP.is_used.is_(False)
        )
        .order_by(OTP.id.desc())
        .first()
    )

    if not otp_entry:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active OTP found")

    # Expiry check
    if now > otp_entry.expiry_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired")

    # Attempt limit check
    if otp_entry.attempt_count >= settings.OTP_MAX_ATTEMPTS:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many incorrect attempts. Request new OTP.")

    # Incorrect OTP
    if otp_entry.otp_code != otp:
        otp_entry.attempt_count += 1
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect OTP")

    # Correct OTP
    otp_entry.is_used = True
    db.commit()

    access_token = create_access_token(
        data={"client_id": client_id_for_otp, "role": role, "email": email}
    )

    refresh_token = create_refresh_token(
        data={"client_id": client_id_for_otp, "role": role, "email": email}
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
