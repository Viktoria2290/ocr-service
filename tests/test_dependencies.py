"""Тесты для зависимостей FastAPI."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastapi import HTTPException, status
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.dependencies import get_current_user


@pytest.mark.asyncio
async def test_get_current_user_success():
    """Тест успешной аутентификации."""
    # Setup
    mock_token = "valid_token"
    mock_db = AsyncMock()
    payload = {"user_id": 1, "email": "test@example.com"}

    mock_user = Mock()
    mock_user.is_active = True

    with patch('app.core.dependencies.decode_token', return_value=payload):
        with patch('app.core.dependencies.get_user', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = mock_user

            # Execute
            result = await get_current_user(token=mock_token, db=mock_db)

    # Assert
    assert result["user_id"] == 1
    assert result["email"] == "test@example.com"
    assert "token_payload" in result


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    """Тест с невалидным токеном."""
    # Setup
    mock_token = "invalid_token"
    mock_db = AsyncMock()

    with patch('app.core.dependencies.decode_token', return_value=None):
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=mock_token, db=mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_get_current_user_missing_fields():
    """Тест с токеном без обязательных полей."""
    # Setup
    mock_token = "invalid_token"
    mock_db = AsyncMock()

    # Test missing user_id
    payload1 = {"email": "test@example.com"}
    with patch('app.core.dependencies.decode_token', return_value=payload1):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=mock_token, db=mock_db)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    # Test missing email
    payload2 = {"user_id": 1}
    with patch('app.core.dependencies.decode_token', return_value=payload2):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=mock_token, db=mock_db)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_user_not_found():
    """Тест с ненайденным пользователем."""
    # Setup
    mock_token = "valid_token"
    mock_db = AsyncMock()
    payload = {"user_id": 999, "email": "test@example.com"}

    with patch('app.core.dependencies.decode_token', return_value=payload):
        with patch('app.core.dependencies.get_user', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = None

            # Execute & Assert
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token=mock_token, db=mock_db)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_user_inactive():
    """Тест с неактивным пользователем."""
    # Setup
    mock_token = "valid_token"
    mock_db = AsyncMock()
    payload = {"user_id": 1, "email": "test@example.com"}

    mock_user = Mock()
    mock_user.is_active = False

    with patch('app.core.dependencies.decode_token', return_value=payload):
        with patch('app.core.dependencies.get_user', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = mock_user

            # Execute & Assert
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token=mock_token, db=mock_db)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED