"""Тесты для бизнес-логики OCR сервиса."""

import pytest
from unittest.mock import Mock, patch, MagicMock, ANY
from PIL import Image
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.business_logic import OCRProcessor, TaskManager


class TestOCRProcessor:
    """Тесты для класса OCRProcessor."""

    @patch('app.core.business_logic.tempfile.NamedTemporaryFile')
    @patch('app.core.business_logic.Image.open')
    @patch('app.core.business_logic.pytesseract.image_to_string')
    @patch('app.core.business_logic.os.unlink')
    @patch('app.core.business_logic.settings')
    def test_process_image_success(self, mock_settings, mock_unlink, mock_image_to_string,
                                   mock_image_open, mock_tempfile):
        """Тест успешной обработки изображения."""
        # Setup
        mock_settings.TESSERACT_LANG = 'rus'

        # Создаем мок для временного файла
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/test.jpg'
        mock_tempfile.return_value.__enter__.return_value = mock_temp

        # Создаем мок для изображения
        mock_image = MagicMock(spec=Image.Image)

        # Настраиваем мок для open, чтобы он возвращал контекстный менеджер с изображением
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = mock_image
        mock_image_open.return_value = mock_context_manager

        mock_image_to_string.return_value = "Extracted text"

        image_data = b"fake_image_data"

        # Execute
        result = OCRProcessor.process_image(image_data, "test.jpg", user_id=1)

        # Assert
        assert result == "Extracted text"
        mock_temp.write.assert_called_once_with(image_data)
        mock_image_open.assert_called_once_with('/tmp/test.jpg')

        # Проверяем, что image_to_string был вызван с любым изображением и правильным lang
        mock_image_to_string.assert_called_once()
        args, kwargs = mock_image_to_string.call_args
        assert kwargs.get('lang') == 'rus'
        # Не проверяем конкретный объект изображения, так как это мок
        assert args[0] is not None

        mock_unlink.assert_called_once_with('/tmp/test.jpg')

    @patch('app.core.business_logic.tempfile.NamedTemporaryFile')
    @patch('app.core.business_logic.Image.open')
    @patch('app.core.business_logic.pytesseract.image_to_string')
    @patch('app.core.business_logic.os.unlink')
    @patch('app.core.business_logic.settings')
    def test_process_image_with_file_object(self, mock_settings, mock_unlink, mock_image_to_string,
                                           mock_image_open, mock_tempfile):
        """Тест обработки файлового объекта."""
        # Setup
        mock_settings.TESSERACT_LANG = 'rus'

        mock_file = Mock()
        mock_file.read.return_value = b"file content"

        mock_temp = MagicMock()
        mock_temp.name = '/tmp/test.jpg'
        mock_tempfile.return_value.__enter__.return_value = mock_temp

        mock_image = MagicMock(spec=Image.Image)
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = mock_image
        mock_image_open.return_value = mock_context_manager

        mock_image_to_string.return_value = "Extracted text"

        # Execute
        result = OCRProcessor.process_image(mock_file, "test.jpg")

        # Assert
        assert result == "Extracted text"
        mock_file.read.assert_called_once()

        # Проверяем, что image_to_string был вызван с правильными параметрами
        mock_image_to_string.assert_called_once()
        args, kwargs = mock_image_to_string.call_args
        assert kwargs.get('lang') == 'rus'
        assert args[0] is not None

    @patch('app.core.business_logic.tempfile.NamedTemporaryFile')
    @patch('app.core.business_logic.Image.open')
    @patch('app.core.business_logic.pytesseract.image_to_string')
    @patch('app.core.business_logic.os.unlink')
    @patch('app.core.business_logic.settings')
    def test_process_image_error(self, mock_settings, mock_unlink, mock_image_to_string,
                                mock_image_open, mock_tempfile):
        """Тест ошибки при обработке изображения."""
        # Setup
        mock_settings.TESSERACT_LANG = 'rus'

        mock_temp = MagicMock()
        mock_temp.name = '/tmp/test.jpg'
        mock_tempfile.return_value.__enter__.return_value = mock_temp

        # Настраиваем исключение при открытии изображения
        mock_image_open.side_effect = Exception("Image error")

        image_data = b"fake_image_data"

        # Execute & Assert
        with pytest.raises(Exception, match="Image error"):
            OCRProcessor.process_image(image_data, "test.jpg")

        mock_unlink.assert_called_once_with('/tmp/test.jpg')

    @patch('app.core.business_logic.tempfile.NamedTemporaryFile')
    @patch('app.core.business_logic.Image.open')
    @patch('app.core.business_logic.pytesseract.image_to_string')
    @patch('app.core.business_logic.os.unlink')
    @patch('app.core.business_logic.settings')
    def test_process_image_unlink_error(self, mock_settings, mock_unlink, mock_image_to_string,
                                       mock_image_open, mock_tempfile):
        """Тест ошибки при удалении временного файла."""
        # Setup
        mock_settings.TESSERACT_LANG = 'rus'

        mock_temp = MagicMock()
        mock_temp.name = '/tmp/test.jpg'
        mock_tempfile.return_value.__enter__.return_value = mock_temp

        mock_image = MagicMock(spec=Image.Image)
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = mock_image
        mock_image_open.return_value = mock_context_manager

        mock_image_to_string.return_value = "Extracted text"
        mock_unlink.side_effect = Exception("Unlink error")

        image_data = b"fake_image_data"

        # Execute - should not raise exception
        result = OCRProcessor.process_image(image_data, "test.jpg")

        # Assert
        assert result == "Extracted text"
        mock_unlink.assert_called_once_with('/tmp/test.jpg')

    @patch('app.core.business_logic.tempfile.NamedTemporaryFile')
    @patch('app.core.business_logic.Image.open')
    @patch('app.core.business_logic.pytesseract.image_to_string')
    @patch('app.core.business_logic.os.unlink')
    @patch('app.core.business_logic.settings')
    def test_process_image_without_user_id(self, mock_settings, mock_unlink, mock_image_to_string,
                                          mock_image_open, mock_tempfile):
        """Тест обработки изображения без user_id."""
        # Setup
        mock_settings.TESSERACT_LANG = 'rus'

        mock_temp = MagicMock()
        mock_temp.name = '/tmp/test.jpg'
        mock_tempfile.return_value.__enter__.return_value = mock_temp

        mock_image = MagicMock(spec=Image.Image)
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = mock_image
        mock_image_open.return_value = mock_context_manager

        mock_image_to_string.return_value = "Extracted text"

        image_data = b"fake_image_data"

        # Execute
        result = OCRProcessor.process_image(image_data, "test.jpg")

        # Assert
        assert result == "Extracted text"
        mock_image_to_string.assert_called_once()
        args, kwargs = mock_image_to_string.call_args
        assert kwargs.get('lang') == 'rus'


class TestTaskManager:
    """Тесты для класса TaskManager."""

    @patch('app.core.business_logic.AsyncResult')
    def test_get_task_status_success(self, mock_async_result):
        """Тест получения статуса успешной задачи."""
        # Setup
        mock_task = MagicMock()
        mock_task.state = "SUCCESS"
        mock_task.ready.return_value = True
        mock_task.result = {"text": "OCR result"}
        mock_async_result.return_value = mock_task

        # Execute
        result = TaskManager.get_task_status("task_123")

        # Assert
        assert result == {
            "task_id": "task_123",
            "status": "SUCCESS",
            "ready": True,
            "result": {"text": "OCR result"}
        }

    @patch('app.core.business_logic.AsyncResult')
    def test_get_task_status_failure(self, mock_async_result):
        """Тест получения статуса упавшей задачи."""
        # Setup
        mock_task = MagicMock()
        mock_task.state = "FAILURE"
        mock_task.ready.return_value = True
        mock_task.info = "Error processing image"
        mock_async_result.return_value = mock_task

        # Execute
        result = TaskManager.get_task_status("task_123")

        # Assert
        assert result == {
            "task_id": "task_123",
            "status": "FAILURE",
            "ready": True,
            "error": "Error processing image"
        }

    @patch('app.core.business_logic.AsyncResult')
    def test_get_task_status_pending(self, mock_async_result):
        """Тест получения статуса ожидающей задачи."""
        # Setup
        mock_task = MagicMock()
        mock_task.state = "PENDING"
        mock_task.ready.return_value = False
        mock_async_result.return_value = mock_task

        # Execute
        result = TaskManager.get_task_status("task_123")

        # Assert
        assert result == {
            "task_id": "task_123",
            "status": "PENDING",
            "ready": False
        }

    @patch('app.core.business_logic.AsyncResult')
    def test_get_task_status_no_info(self, mock_async_result):
        """Тест получения статуса упавшей задачи без info."""
        # Setup
        mock_task = MagicMock()
        mock_task.state = "FAILURE"
        mock_task.ready.return_value = True
        mock_task.info = None
        mock_async_result.return_value = mock_task

        # Execute
        result = TaskManager.get_task_status("task_123")

        # Assert
        assert result == {
            "task_id": "task_123",
            "status": "FAILURE",
            "ready": True,
            "error": "Unknown error"
        }