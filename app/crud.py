"""Асинхронные и синхронные CRUD операции."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select
from app import models, schemas
from typing import Optional
import logging

logger = logging.getLogger(__name__)


async def get_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    """Получает пользователя по ID."""
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    """Получает пользователя по email."""
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, email: str, hashed_password: str) -> models.User:
    """Создает нового пользователя."""
    user = models.User(email=email, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_image_text(db: AsyncSession, image_id: int) -> Optional[models.ImageText]:
    """Получает запись о тексте изображения по ID изображения."""
    result = await db.execute(select(models.ImageText).where(models.ImageText.image_id == image_id))
    return result.scalar_one_or_none()


async def create_image_text(db: AsyncSession, image_text: schemas.ImageTextCreate) -> models.ImageText:
    """Создает новую запись о тексте изображения."""
    existing = await get_image_text(db, image_text.image_id)
    if existing:
        for key, value in image_text.model_dump().items():
            setattr(existing, key, value)
        await db.commit()
        await db.refresh(existing)
        return existing

    db_image_text = models.ImageText(**image_text.model_dump())
    db.add(db_image_text)
    await db.commit()
    await db.refresh(db_image_text)
    return db_image_text


async def update_image_text(
    db: AsyncSession, image_id: int, update_data: schemas.ImageTextUpdate
) -> Optional[models.ImageText]:
    """Обновляет запись о тексте изображения."""
    db_image_text = await get_image_text(db, image_id)
    if db_image_text:
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(db_image_text, key, value)
        await db.commit()
        await db.refresh(db_image_text)
    return db_image_text


async def delete_image_text(db: AsyncSession, image_id: int) -> bool:
    """Удаляет запись о тексте изображения."""
    db_image_text = await get_image_text(db, image_id)
    if db_image_text:
        await db.delete(db_image_text)
        await db.commit()
        return True
    return False


def get_image_text_sync(db: Session, image_id: int) -> Optional[models.ImageText]:
    """Синхронная версия получения записи о тексте изображения."""
    return db.query(models.ImageText).filter(models.ImageText.image_id == image_id).first()


def update_image_text_sync(
    db: Session, image_id: int, update_data: schemas.ImageTextUpdate
) -> Optional[models.ImageText]:
    """Синхронная версия обновления записи о тексте изображения."""
    db_image_text = get_image_text_sync(db, image_id)
    if db_image_text:
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(db_image_text, key, value)
        db.commit()
        db.refresh(db_image_text)
    return db_image_text