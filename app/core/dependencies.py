"""Зависимости для FastAPI эндпоинтов."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud import get_user
from app.core.security import decode_token
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Получает данные текущего пользователя из JWT токена."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        logger.warning("Невалидный JWT токен")
        raise credentials_exception

    user_id = payload.get("user_id")
    email = payload.get("email")

    if user_id is None or email is None:
        logger.warning("JWT токен не содержит user_id или email")
        raise credentials_exception

    user = await get_user(db, user_id)
    if user is None or not user.is_active:
        logger.warning(f"Пользователь {user_id} не найден или не активен")
        raise credentials_exception

    logger.info(f"Пользователь аутентифицирован: {email}")
    return {"user_id": user_id, "email": email, "token_payload": payload}