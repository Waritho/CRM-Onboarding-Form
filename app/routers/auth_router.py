from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from sqlalchemy.orm import Session
from typing import Callable

from app.database import get_db
from app.schemas.auth_schema import SendOTPRequest, VerifyOTPRequest
from app.services.auth_service import send_otp_service, verify_otp_service
from app.utils.jwt_handler import decode_token, create_access_token


class AuthRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        
        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except RequestValidationError as exc:
                errors = exc.errors()
                error_msg = errors[0].get("msg", "Validation error") if errors else "Validation error"
                if "valid email address" in error_msg.lower():
                    error_msg = "Invalid email address."
                raise HTTPException(status_code=422, detail=error_msg)
                
        return custom_route_handler

router = APIRouter(prefix="/auth", tags=["Auth"], route_class=AuthRoute)

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
    role = payload.get("role", "primary") # default to primary for legacy tokens

    new_access_token = create_access_token(
        data={"client_id": client_id, "role": role}
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }