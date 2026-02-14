"""Модели SQLAlchemy для базы данных."""

from sqlalchemy import Column, Integer, Text, String, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """Модель пользователя."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    image_texts = relationship("ImageText", back_populates="user", cascade="all, delete-orphan")


class ImageText(Base):
    """Модель для хранения результатов OCR."""

    __tablename__ = "image_text"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    text = Column(Text)
    status = Column(String(20), default="pending")
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="image_texts")

    __table_args__ = (UniqueConstraint("image_id", name="uq_image_text_image_id"),)