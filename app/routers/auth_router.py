from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth_schema import SendOTPRequest, VerifyOTPRequest
from app.services.auth_service import send_otp_service, verify_otp_service
from app.utils.jwt_handler import decode_token, create_access_token


router = APIRouter(prefix="/auth", tags=["Auth"]
)


# SEND OTP
@router.post("/send-otp")
def send_otp(
    data: SendOTPRequest,
    db: Session = Depends(get_db)
):
    return send_otp_service(data.email, db)


# VERIFY OTP (LOGIN)
@router.post("/verify-otp")
def verify_otp(
    data: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    return verify_otp_service(data.email, data.otp, db)


# REFRESH ACCESS TOKEN
@router.post("/refresh-token")
def refresh_token(refresh_token: str):

    payload = decode_token(refresh_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    client_id = payload.get("client_id")

    new_access_token = create_access_token(
        data={"client_id": client_id}
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }