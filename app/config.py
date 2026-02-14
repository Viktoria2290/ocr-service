"""Конфигурация приложения."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Настройки приложения."""

    DATABASE_URL: str = "postgresql://ocr_user:ocr_pass@postgres:5432/ocr_db"

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    TESSERACT_LANG: str = "rus+eng"
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    LOG_LEVEL: str = "INFO"

    JWT_SECRET_KEY: str = "jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    UPLOAD_DIR: str = "/app/uploads"

    class Config:
        env_file = ".env"
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = self.RABBITMQ_URL
        if not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = self.RABBITMQ_URL.replace("amqp://", "rpc://")


settings = Settings()