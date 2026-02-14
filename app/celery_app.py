"""Конфигурация Celery."""

from celery import Celery
from app.config import settings
import logging

logger = logging.getLogger(__name__)

celery_app = Celery(
    "ocr_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Europe/Moscow",
    enable_utc=True,
    broker_connection_timeout=30,
    broker_connection_retry=True,
    broker_connection_max_retries=3,
    task_time_limit=60,
    task_soft_time_limit=50,
    task_default_queue="celery",
    result_expires=3600,
    task_track_started=True,
)

logger.info("Celery app создан")

__all__ = ["celery_app"]