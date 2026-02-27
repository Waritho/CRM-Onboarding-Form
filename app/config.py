from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:Shubh%402311@localhost:5432/CRM"

    OTP_EXPIRY_MINUTES: int = 2
    OTP_MAX_ATTEMPTS: int = 3
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()