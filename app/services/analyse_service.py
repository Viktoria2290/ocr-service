"""Сервис для запуска OCR анализа."""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas
from app.core.file_storage import FileStorage
from app.tasks import process_ocr_task
import logging

logger = logging.getLogger(__name__)
file_storage = FileStorage()


class AnalyseService:
    """Сервис для обработки OCR анализа."""

    async def process_analyse(self, image_id: int, user_id: int, db: AsyncSession) -> dict:
        """Запускает OCR анализ для изображения."""
        logger.info(f"Запуск OCR анализа - user_id: {user_id}, image_id: {image_id}")

        file_info = file_storage.get_file_info(image_id, user_id)
        if not file_info:
            logger.warning(f"Файл не найден - image_id: {image_id}")
            raise HTTPException(404, "Image not found")

        existing = await crud.get_image_text(db, image_id)
        if existing and existing.user_id != user_id:
            logger.warning(f"Попытка доступа к чужому ресурсу - image_id: {image_id}")
            raise HTTPException(403, "Access denied")

        if existing:
            await crud.update_image_text(
                db, image_id, schemas.ImageTextUpdate(status="pending", text=None, error_message=None)
            )
        else:
            await crud.create_image_text(db, schemas.ImageTextCreate(image_id=image_id, user_id=user_id))

        try:
            with open(file_info["file_path"], "rb") as f:
                image_data = f.read()

            task = process_ocr_task.apply_async(
                args=[image_id, image_data, file_info["filename"], user_id],
                queue="celery",
                time_limit=60,
                soft_time_limit=50,
            )

            logger.info(f"Задача OCR отправлена - Task ID: {task.id}")
            return {
                "task_id": str(task.id),
                "image_id": image_id,
                "status": "processing",
                "message": "OCR processing started",
            }
        except Exception as e:
            error_msg = f"Celery error: {str(e)}"
            logger.error(f"Ошибка отправки задачи: {e}")
            await crud.update_image_text(
                db, image_id, schemas.ImageTextUpdate(status="failed", error_message=error_msg[:500])
            )
            raise HTTPException(503, f"OCR service unavailable: {str(e)}")