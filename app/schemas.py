"""Pydantic схемы для валидации и сериализации данных."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Базовая схема пользователя."""

    email: EmailStr


class UserCreate(UserBase):
    """Схема для создания пользователя."""

    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    """Схема для ответа с данными пользователя."""

    id: int
    is_active: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Схема для ответа с токеном."""

    access_token: str
    token_type: str = "bearer"


class ImageTextBase(BaseModel):
    """Базовая схема для результата OCR."""

    image_id: int
    user_id: int


class ImageTextCreate(ImageTextBase):
    """Схема для создания записи OCR."""


class ImageTextUpdate(BaseModel):
    """Схема для обновления записи OCR."""

    text: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None


class ImageTextResponse(ImageTextBase):
    """Схема для ответа с результатом OCR."""

    id: int
    text: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True