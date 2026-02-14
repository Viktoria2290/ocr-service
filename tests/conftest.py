import sys
import os
from pathlib import Path
from unittest.mock import patch
import pytest

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Мокаем создание директорий для всех тестов
@pytest.fixture(autouse=True)
def mock_file_system():
    """Мокаем файловые операции для всех тестов."""
    with patch('pathlib.Path.mkdir'), \
         patch('app.core.file_storage.FileStorage._ensure_upload_dir'):
        yield