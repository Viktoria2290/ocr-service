"""Сервис для удаления файлов и записей."""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud
from app.core.file_storage import FileStorage
import logging

logger = logging.getLogger(__name__)
file_storage = FileStorage()


class DeleteService:
    """Сервис для обработки удаления."""

    async def process_delete(self, image_id: int, user_id: int, db: AsyncSession) -> dict:
        """Удаляет изображение и запись из БД."""
        logger.info(f"Удаление - user_id: {user_id}, image_id: {image_id}")

        image_text = await crud.get_image_text(db, image_id)
        if image_text and image_text.user_id != user_id:
            logger.warning(f"Попытка удаления чужого ресурса - image_id: {image_id}")
            raise HTTPException(403, "Access denied")

        db_deleted = await crud.delete_image_text(db, image_id)
        file_deleted = file_storage.delete_file(image_id, user_id)

        if not db_deleted and not file_deleted:
            logger.warning(f"Запись не найдена - image_id: {image_id}")
            raise HTTPException(404, "Record not found")

        return {
            "message": "OCR record deleted from database" + (" and file deleted" if file_deleted else ""),
            "image_id": image_id,
            "db_record_deleted": db_deleted,
            "file_deleted": file_deleted,
        }