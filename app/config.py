from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")

    # OTP
    OTP_EXPIRY_MINUTES: int = Field(default=2, env="OTP_EXPIRY_MINUTES")
    OTP_MAX_ATTEMPTS: int = Field(default=3, env="OTP_MAX_ATTEMPTS")

    # Access Token
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60,
        env="ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()