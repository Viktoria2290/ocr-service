"""Тесты для эндпоинтов API."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastapi import UploadFile
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Мокаем FileStorage до импорта endpoints
with patch('app.core.file_storage.FileStorage._ensure_upload_dir'):
    from app.api.endpoints import upload_document, doc_analyse, delete_doc, get_text, get_status


@pytest.mark.asyncio
async def test_upload_document():
    """Тест эндпоинта загрузки документа."""
    # Setup
    mock_file = Mock(spec=UploadFile)
    mock_file.filename = "test.jpg"
    mock_db = AsyncMock()
    mock_current_user = {"user_id": 1}

    mock_service = AsyncMock()
    mock_service.process_upload.return_value = {"id": 1, "filename": "test.jpg"}

    with patch('app.api.endpoints.UploadService', return_value=mock_service):
        # Execute
        result = await upload_document(
            file=mock_file,
            db=mock_db,
            current_user=mock_current_user
        )

    # Assert
    assert result == {"id": 1, "filename": "test.jpg"}
    mock_service.process_upload.assert_called_once_with(mock_file, 1, mock_db)


@pytest.mark.asyncio
async def test_doc_analyse():
    """Тест эндпоинта анализа документа."""
    # Setup
    mock_db = AsyncMock()
    mock_current_user = {"user_id": 1}
    image_id = 123

    mock_service = AsyncMock()
    mock_service.process_analyse.return_value = {"task_id": "task_123"}

    with patch('app.api.endpoints.AnalyseService', return_value=mock_service):
        # Execute
        result = await doc_analyse(
            image_id=image_id,
            db=mock_db,
            current_user=mock_current_user
        )

    # Assert
    assert result == {"task_id": "task_123"}
    mock_service.process_analyse.assert_called_once_with(image_id, 1, mock_db)


@pytest.mark.asyncio
async def test_delete_doc():
    """Тест эндпоинта удаления документа."""
    # Setup
    mock_db = AsyncMock()
    mock_current_user = {"user_id": 1}
    image_id = 123

    mock_service = AsyncMock()
    mock_service.process_delete.return_value = {"message": "Deleted successfully"}

    with patch('app.api.endpoints.DeleteService', return_value=mock_service):
        # Execute
        result = await delete_doc(
            image_id=image_id,
            db=mock_db,
            current_user=mock_current_user
        )

    # Assert
    assert result == {"message": "Deleted successfully"}
    mock_service.process_delete.assert_called_once_with(image_id, 1, mock_db)


@pytest.mark.asyncio
async def test_get_text():
    """Тест эндпоинта получения текста."""
    # Setup
    mock_db = AsyncMock()
    mock_current_user = {"user_id": 1}
    image_id = 123

    mock_service = AsyncMock()
    mock_service.get_text.return_value = {"text": "OCR result"}

    with patch('app.api.endpoints.TextService', return_value=mock_service):
        # Execute
        result = await get_text(
            image_id=image_id,
            db=mock_db,
            current_user=mock_current_user
        )

    # Assert
    assert result == {"text": "OCR result"}
    mock_service.get_text.assert_called_once_with(image_id, 1, mock_db)


@pytest.mark.asyncio
async def test_get_status():
    """Тест эндпоинта получения статуса."""
    # Setup
    mock_current_user = {"user_id": 1}
    task_id = "task_123"

    mock_service = AsyncMock()
    mock_service.get_status.return_value = {"status": "SUCCESS", "task_id": task_id}

    with patch('app.api.endpoints.StatusService', return_value=mock_service):
        # Execute
        result = await get_status(
            task_id=task_id,
            current_user=mock_current_user
        )

    # Assert
    assert result == {"status": "SUCCESS", "task_id": task_id}
    mock_service.get_status.assert_called_once_with(task_id, 1)