"""Функции для безопасности: хеширование паролей, создание и проверка JWT."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import bcrypt
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля хешу используя bcrypt напрямую."""
    try:
        password_bytes = plain_password.encode('utf-8')
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        logger.error(f"Ошибка при проверке пароля: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Создает хеш пароля используя bcrypt напрямую."""
    try:
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"Ошибка при хешировании пароля: {e}")
        raise


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Создает JWT токен доступа."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Ошибка при создании токена: {e}")
        raise


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Декодирует и проверяет JWT токен."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Токен просрочен")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Невалидный токен: {e}")
        return None
    except Exception as e:
        logger.error(f"Неожиданная ошибка при декодировании токена: {e}")
        return None