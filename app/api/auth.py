"""Эндпоинты для аутентификации."""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import schemas
from app.crud import get_user_by_email, create_user
from app.core.security import create_access_token, verify_password, get_password_hash
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    email: str = Form(..., description="Email пользователя"),
    password: str = Form(..., description="Пароль (минимум 6 символов)"),
    db: AsyncSession = Depends(get_db),
):
    """Регистрация нового пользователя."""
    logger.info(f"Регистрация пользователя: {email}")

    if len(password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")

    existing_user = await get_user_by_email(db, email)
    if existing_user:
        logger.warning(f"Email уже зарегистрирован: {email}")
        raise HTTPException(400, "Email already registered")

    hashed_password = get_password_hash(password)
    user = await create_user(db, email, hashed_password)

    logger.info(f"Пользователь зарегистрирован: {email}")
    return user


@router.post("/login", response_model=schemas.TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """Вход в систему. username: email пользователя, password: пароль."""
    logger.info(f"Вход пользователя: {form_data.username}")

    user = await get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Неудачная попытка входа: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        logger.warning(f"Попытка входа неактивного пользователя: {form_data.username}")
        raise HTTPException(403, "User is deactivated")

    access_token = create_access_token(data={"user_id": user.id, "email": user.email})
    logger.info(f"Пользователь вошел: {user.email}")
    return schemas.TokenResponse(access_token=access_token)