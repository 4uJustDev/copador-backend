from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from app.routers import auth, category, product, carpet, role, product_type
from starlette.staticfiles import StaticFiles
import os
from app.config import MEDIA_ROOT
from app.core.exceptions import (
    ValidationError,
    NotFoundError,
    ConflictError,
    DatabaseError,
    BusinessLogicError,
)


app = FastAPI(root_path="/api/project2", title="Product Catalog API")

app.include_router(auth.router)
app.include_router(category.router)
app.include_router(product.router)
app.include_router(carpet.router)
app.include_router(role.router)
app.include_router(product_type.router)


@app.get("/")
def root():
    """Корневой эндпоинт"""
    return {
        "message": "Product Catalog API is working",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    """Эндпоинт для проверки здоровья приложения"""
    return {"status": "healthy"}


@app.exception_handler(HTTPException)
async def http_exception_handler(_request, exc):
    """Глобальный обработчик HTTP исключений"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(_request, exc):
    """Обработчик ошибок валидации"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "type": "validation_error"},
    )


@app.exception_handler(NotFoundError)
async def not_found_exception_handler(_request, exc):
    """Обработчик ошибок - ресурс не найден"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "type": "not_found"},
    )


@app.exception_handler(ConflictError)
async def conflict_exception_handler(_request, exc):
    """Обработчик ошибок конфликта"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "type": "conflict"},
    )


@app.exception_handler(DatabaseError)
async def database_exception_handler(_request, exc):
    """Обработчик ошибок базы данных"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "type": "database_error"},
    )


@app.exception_handler(BusinessLogicError)
async def business_logic_exception_handler(_request, exc):
    """Обработчик ошибок бизнес-логики"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "type": "business_logic_error"},
    )


@app.exception_handler(Exception)
async def general_exception_handler(_request, exc):
    """Общий обработчик исключений"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Внутренняя ошибка сервера",
            "detail": str(exc) if app.debug else "Произошла непредвиденная ошибка",
            "type": "internal_server_error",
        },
    )


# Static files for media (user-uploaded content)
os.makedirs(MEDIA_ROOT, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_ROOT), name="media")
