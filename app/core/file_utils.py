"""Утилиты для работы с файлами."""

import os
from typing import Set

ALLOWED_EXTENSIONS: Set[str] = {'.jpg', '.jpeg', '.png'}


def is_image_file(filename: str) -> bool:
    """Проверяет, является ли файл изображением допустимого формата."""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS