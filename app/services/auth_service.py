from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.models.client import Client
from app.models.otp import OTP
from app.utils.otp_generator import generate_otp
from app.utils.jwt_handler import create_access_token, create_refresh_token
from app.config import settings


# SEND OTP
def send_otp_service(email: str, db: Session):
    # Get or create client
    client = db.query(Client).filter(Client.email == email).first()

    if not client:
        client = Client(email=email)
        db.add(client)
        db.commit()
        db.refresh(client)

    now = datetime.now(timezone.utc)

    # Check for existing valid OTP
    existing_otp = (
        db.query(OTP)
        .filter(
            OTP.client_id == client.id,
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
        client_id=client.id,
        otp_code=otp_code,
        expiry_at=expiry,
        attempt_count=0,
        is_used=False
    )

    db.add(otp_entry)
    db.commit()

    # TODO: replace with real email sender
    print(f"OTP for {email}: {otp_code}")

    return {"message": "OTP sent successfully"}


# VERIFY OTP
def verify_otp_service(email: str, otp: str, db: Session):
    client = db.query(Client).filter(Client.email == email).first()

    if not client:
        return {"error": "Invalid email"}

    now = datetime.now(timezone.utc)

    # Get latest unused OTP
    otp_entry = (
        db.query(OTP)
        .filter(
            OTP.client_id == client.id,
            OTP.is_used.is_(False)
        )
        .order_by(OTP.id.desc())
        .first()
    )

    if not otp_entry:
        return {"error": "No active OTP found"}

    # Expiry check
    if now > otp_entry.expiry_at:
        return {"error": "OTP expired"}

    # Attempt limit check
    if otp_entry.attempt_count >= settings.OTP_MAX_ATTEMPTS:
        return {"error": "Too many incorrect attempts. Request new OTP."}

    # Incorrect OTP
    if otp_entry.otp_code != otp:
        otp_entry.attempt_count += 1
        db.commit()
        return {"error": "Incorrect OTP"}

    # Correct OTP
    otp_entry.is_used = True
    db.commit()

    access_token = create_access_token(
        data={"client_id": client.id}
    )

    refresh_token = create_refresh_token(
        data={"client_id": client.id}
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }