"""Асинхронная и синхронная конфигурация базы данных."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy import create_engine
from app.config import settings
import logging

logger = logging.getLogger(__name__)

async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600,
)

sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    """Асинхронная зависимость для получения сессии базы данных."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db() -> Session:
    """Синхронная зависимость для получения сессии базы данных (для Celery)."""
    db = SyncSessionLocal()
    try:
        return db
    finally:
        db.close()