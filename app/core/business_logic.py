"""Бизнес-логика для OCR сервиса."""

import os
import tempfile
from typing import Dict, Any
from PIL import Image
import pytesseract
from app.config import settings
import logging
from celery.result import AsyncResult

logger = logging.getLogger(__name__)


class OCRProcessor:
    """Класс для обработки OCR операций."""

    @staticmethod
    def process_image(image_data, filename: str, user_id: int = None) -> str:
        """Обрабатывает изображение и извлекает текст."""
        if hasattr(image_data, "read"):
            image_data = image_data.read()

        file_ext = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp_file:
            tmp_file.write(image_data)
            tmp_path = tmp_file.name

        try:
            image = Image.open(tmp_path)
            text = pytesseract.image_to_string(image, lang=settings.TESSERACT_LANG)
            logger.info(f"OCR выполнен - user_id: {user_id}, длина текста: {len(text)}")
            return text.strip()
        except Exception as e:
            logger.error(f"Ошибка OCR: {e}")
            raise
        finally:
            try:
                os.unlink(tmp_path)
            except:
                pass


class TaskManager:
    """Класс для управления задачами Celery."""

    @staticmethod
    def get_task_status(task_id: str) -> Dict[str, Any]:
        """Получает статус задачи Celery."""
        from app.tasks import process_ocr_task
        task = AsyncResult(task_id, app=process_ocr_task.app)

        response = {"task_id": task_id, "status": task.state, "ready": task.ready()}

        if task.state == "SUCCESS":
            response["result"] = task.result
        elif task.state == "FAILURE":
            response["error"] = str(task.info) if task.info else "Unknown error"

        return response