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

    # ====== NEW: ZeptoMail ======
    ZEPTOMAIL_API_URL: str = Field(default="https://api.zeptomail.in/v1.1/email", env="ZEPTOMAIL_API_URL")
    ZEPTOMAIL_API_TOKEN: str = Field(..., env="ZEPTOMAIL_API_TOKEN")
    ZEPTOMAIL_FROM_EMAIL: str = Field(default="accounts@info.zylker.com", env="ZEPTOMAIL_FROM_EMAIL")
    ZEPTOMAIL_FROM_NAME: str = Field(default="Paula", env="ZEPTOMAIL_FROM_NAME")

    # ====== NEW: Celery + Redis ======
    CELERY_BROKER_URL: str = Field(default="redis://127.0.0.1:6379/0", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://127.0.0.1:6379/1", env="CELERY_RESULT_BACKEND")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
