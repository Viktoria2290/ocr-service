"""Сервис для получения статуса задачи."""

from app.core.business_logic import TaskManager
import logging

logger = logging.getLogger(__name__)


class StatusService:
    """Сервис для получения статуса задачи OCR."""

    async def get_status(self, task_id: str, user_id: int) -> dict:
        """Получает статус задачи по ID."""
        logger.info(f"Запрос статуса задачи - user_id: {user_id}, task_id: {task_id}")

        try:
            response = TaskManager.get_task_status(task_id)
            logger.info(f"Статус задачи: {response['status']}")
            return response
        except Exception as e:
            logger.error(f"Ошибка проверки статуса: {e}")
            return {"task_id": task_id, "status": "UNKNOWN", "error": str(e)}