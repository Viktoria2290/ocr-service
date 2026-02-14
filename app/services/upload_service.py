"""Сервис для загрузки файлов."""

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.file_storage import FileStorage
from app.core.file_utils import is_image_file
import logging

logger = logging.getLogger(__name__)
file_storage = FileStorage()


class UploadService:
    """Сервис для обработки загрузки файлов."""

    async def process_upload(self, file: UploadFile, user_id: int, db: AsyncSession) -> dict:
        """Обрабатывает загрузку файла."""
        logger.info(f"Обработка загрузки - user_id: {user_id}, filename: {file.filename}")

        if not is_image_file(file.filename):
            logger.warning(f"Неверный формат файла: {file.filename}")
            raise HTTPException(400, "Only jpg, jpeg, png files allowed")

        try:
            contents = await file.read()
            image_id = await file_storage.save_file(contents, file.filename, user_id)

            logger.info(f"Файл обработан - image_id: {image_id}, user_id: {user_id}")
            return {
                "message": "File uploaded successfully",
                "image_id": image_id,
                "filename": file.filename,
                "next_step": "Use /doc_analyse to start OCR processing",
            }
        except Exception as e:
            logger.error(f"Ошибка загрузки: {e}")
            raise HTTPException(500, f"Upload failed: {str(e)}")