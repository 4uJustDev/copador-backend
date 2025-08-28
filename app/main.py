from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from app.routers import auth, category, product, carpet, role
from starlette.staticfiles import StaticFiles
import os
from app.config import MEDIA_ROOT


app = FastAPI(root_path="/api/project2", title="Product Catalog API")

app.include_router(auth.router)
app.include_router(category.router)
app.include_router(product.router)
app.include_router(carpet.router)
app.include_router(role.router)


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


# Static files for media (user-uploaded content)
os.makedirs(MEDIA_ROOT, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_ROOT), name="media")
