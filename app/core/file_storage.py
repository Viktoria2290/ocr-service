"""Управление файловым хранилищем для загруженных изображений."""

import os
import hashlib
import time
from typing import Optional, Dict, Any
from pathlib import Path
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class FileStorage:
    """Класс для управления файловым хранилищем."""

    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.allowed_extensions = {'.jpg', '.jpeg', '.png'}
        self._ensure_upload_dir()

    def _ensure_upload_dir(self):
        """Создает директорию для загрузок."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _get_user_dir(self, user_id: int) -> Path:
        """Возвращает путь к директории пользователя."""
        user_dir = self.upload_dir / str(user_id)
        user_dir.mkdir(exist_ok=True)
        return user_dir

    def _generate_image_id(self, filename: str, user_id: int) -> int:
        """Генерирует уникальный ID для изображения."""
        timestamp = int(time.time() * 1000)
        hash_input = f"{filename}_{user_id}_{timestamp}".encode()
        return int(hashlib.md5(hash_input).hexdigest()[:8], 16) % (2 ** 31 - 1)

    def is_allowed_file(self, filename: str) -> bool:
        """Проверяет, разрешен ли тип файла."""
        ext = Path(filename).suffix.lower()
        return ext in self.allowed_extensions

    async def save_file(self, file_data: bytes, filename: str, user_id: int) -> int:
        """Сохраняет файл на диск."""
        image_id = self._generate_image_id(filename, user_id)
        ext = Path(filename).suffix
        safe_filename = f"{image_id}{ext}"
        file_path = self._get_user_dir(user_id) / safe_filename

        with open(file_path, 'wb') as f:
            f.write(file_data)

        logger.info(f"Файл сохранен: {file_path}, image_id: {image_id}")
        return image_id

    def get_file_path(self, image_id: int, filename: str, user_id: int) -> str:
        """Возвращает путь к файлу."""
        ext = Path(filename).suffix
        safe_filename = f"{image_id}{ext}"
        return str(self._get_user_dir(user_id) / safe_filename)

    def get_file_info(self, image_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Получает информацию о файле."""
        user_dir = self._get_user_dir(user_id)

        for ext in self.allowed_extensions:
            file_path = user_dir / f"{image_id}{ext}"
            if file_path.exists():
                return {
                    "image_id": image_id,
                    "file_path": str(file_path),
                    "filename": f"{image_id}{ext}",
                }
        return None

    def delete_file(self, image_id: int, user_id: int) -> bool:
        """Удаляет файл."""
        user_dir = self._get_user_dir(user_id)

        for ext in self.allowed_extensions:
            file_path = user_dir / f"{image_id}{ext}"
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Файл удален: {file_path}")
                return True

        return False