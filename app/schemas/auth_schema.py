from pydantic import BaseModel, EmailStr


# SEND OTP REQUEST
class SendOTPRequest(BaseModel):
    email: EmailStr


# VERIFY OTP REQUEST
class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str


# AUTH RESPONSE
class AuthResponse(BaseModel):
    message: str
    client_id: int | None = None