"""Асинхронные эндпоинты API для OCR сервиса."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import schemas
from app.core.dependencies import get_current_user
from app.services.upload_service import UploadService
from app.services.analyse_service import AnalyseService
from app.services.delete_service import DeleteService
from app.services.text_service import TextService
from app.services.status_service import StatusService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Загрузка изображения для OCR анализа."""
    service = UploadService()
    return await service.process_upload(file, current_user["user_id"], db)


@router.post("/doc_analyse")
async def doc_analyse(
    image_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Запуск OCR анализа для загруженного изображения."""
    service = AnalyseService()
    return await service.process_analyse(image_id, current_user["user_id"], db)


@router.delete("/doc_delete/{image_id}")
async def delete_doc(
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Удаление изображения и результата OCR."""
    service = DeleteService()
    return await service.process_delete(image_id, current_user["user_id"], db)


@router.get("/get_text/{image_id}")
async def get_text(
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Получение результата OCR анализа."""
    service = TextService()
    return await service.get_text(image_id, current_user["user_id"], db)


@router.get("/status/{task_id}")
async def get_status(task_id: str, current_user: dict = Depends(get_current_user)):
    """Получение статуса задачи OCR."""
    service = StatusService()
    return await service.get_status(task_id, current_user["user_id"])