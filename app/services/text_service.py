"""Сервис для получения текста."""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud
import logging

logger = logging.getLogger(__name__)


class TextService:
    """Сервис для получения результата OCR."""

    async def get_text(self, image_id: int, user_id: int, db: AsyncSession) -> dict:
        """Получает текст из OCR результата."""
        logger.info(f"Запрос результата OCR - user_id: {user_id}, image_id: {image_id}")

        image_text = await crud.get_image_text(db, image_id)
        if not image_text:
            logger.warning(f"Запись не найдена - image_id: {image_id}")
            raise HTTPException(404, "Text not found for this image")

        if image_text.user_id != user_id:
            logger.warning(f"Попытка доступа к чужому ресурсу - image_id: {image_id}")
            raise HTTPException(403, "Access denied")

        return {
            "image_id": image_id,
            "text": image_text.text,
            "status": image_text.status,
            "error_message": image_text.error_message,
            "created_at": image_text.created_at.isoformat() if image_text.created_at else None,
        }