"""Основной модуль FastAPI приложения."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.endpoints import router as api_router
from app.api.auth import router as auth_router
from app.core.logging_config import setup_logging
import logging
import os
import subprocess
from sqlalchemy import text

setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="OCR Service API",
    description="Сервис для извлечения текста из изображений",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Аутентификация"])
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Корневой эндпоинт с информацией о API."""
    return {
        "message": "OCR Service API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "register": "POST /auth/register - Регистрация по email и паролю",
            "login": "POST /auth/login - Вход по email и паролю (получение токена)",
            "upload": f"POST {settings.API_V1_PREFIX}/upload - Загрузить изображение",
            "doc_analyse": f"POST {settings.API_V1_PREFIX}/doc_analyse - Запустить OCR анализ",
            "get_text": f"GET {settings.API_V1_PREFIX}/get_text/{{image_id}} - Получить результат OCR",
            "delete": f"DELETE {settings.API_V1_PREFIX}/doc_delete/{{image_id}} - Удалить изображение",
            "status": f"GET {settings.API_V1_PREFIX}/status/{{task_id}} - Статус задачи OCR",
        },
    }


@app.get("/health")
async def health():
    """Эндпоинт для проверки здоровья сервиса."""
    return {"status": "healthy"}


async def run_migrations():
    """Запускает миграции Alembic при старте приложения."""
    try:
        logger.info("Применение миграций Alembic...")

        versions_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'alembic', 'versions')

        if not os.listdir(versions_dir):
            logger.info("Создание новой миграции...")
            create_result = subprocess.run(
                ["alembic", "revision", "--autogenerate", "-m", "initial"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(__file__))
            )

            if create_result.returncode == 0:
                logger.info("Миграция создана")
            else:
                logger.error(f"Ошибка создания миграции: {create_result.stderr}")

        logger.info("Применение миграций...")
        upgrade_result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )

        if upgrade_result.returncode == 0:
            logger.info("Миграции успешно применены")
        else:
            logger.error(f"Ошибка применения миграций: {upgrade_result.stderr}")

        from app.database import async_engine
        async with async_engine.connect() as conn:
            result = await conn.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')")
            )
            if result.scalar():
                logger.info("Таблица 'users' существует")
            else:
                logger.error("Таблица 'users' не создана")

            result = await conn.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'image_text')")
            )
            if result.scalar():
                logger.info("Таблица 'image_text' существует")
            else:
                logger.error("Таблица 'image_text' не создана")

    except Exception as e:
        logger.error(f"Критическая ошибка миграций: {e}")
        raise


@app.on_event("startup")
async def startup_event():
    """Действия при запуске приложения."""
    logger.info("Запуск OCR сервиса")
    await run_migrations()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info(f"Директория загрузок: {settings.UPLOAD_DIR}")
    logger.info(f"Документация: http://localhost:{settings.PORT}/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Действия при остановке приложения."""
    logger.info("Остановка OCR сервиса")
    from app.database import async_engine
    await async_engine.dispose()
    logger.info("Соединения с БД закрыты")