"""Задачи Celery для обработки OCR."""

from app.celery_app import celery_app
from app.database import get_sync_db
from app import crud, schemas
from app.core.business_logic import OCRProcessor
import logging
import io

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.process_ocr_task", time_limit=60, soft_time_limit=50)
def process_ocr_task(self, image_id: int, image_data: bytes, filename: str, user_id: int = None):
    """Задача OCR обработки изображения."""
    db = get_sync_db()

    try:
        logger.info(f"Начало обработки OCR - image_id: {image_id}, user_id: {user_id}")

        crud.update_image_text_sync(db, image_id, schemas.ImageTextUpdate(status="processing"))
        db.commit()

        try:
            image_bytes_io = io.BytesIO(image_data)
            extracted_text = OCRProcessor.process_image(image_bytes_io, filename, user_id)
            status = "completed"
        except Exception as ocr_error:
            logger.error(f"Ошибка OCR: {ocr_error}", exc_info=True)
            extracted_text = None
            status = "failed"

        crud.update_image_text_sync(
            db,
            image_id,
            schemas.ImageTextUpdate(
                text=extracted_text,
                status=status,
                error_message=str(ocr_error) if status == "failed" else None,
            ),
        )
        db.commit()

        return {
            "image_id": image_id,
            "user_id": user_id,
            "status": status,
            "text_length": len(extracted_text) if extracted_text else 0,
        }

    except Exception as e:
        logger.error(f"Критическая ошибка OCR: {e}", exc_info=True)
        try:
            crud.update_image_text_sync(
                db, image_id, schemas.ImageTextUpdate(status="failed", error_message=str(e)[:500])
            )
            db.commit()
        except:
            db.rollback()
        raise
    finally:
        db.close()