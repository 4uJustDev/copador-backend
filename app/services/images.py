import os
from pathlib import Path
from PIL import Image
from typing import Tuple
from app.config import MEDIA_ROOT


def create_thumbnail(
    original_path: str, thumb_path: str, size: Tuple[int, int] = (300, 300)
) -> bool:
    """Создать миниатюру изображения"""
    try:
        with Image.open(original_path) as img:
            # Конвертируем в RGB если нужно
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            # Изменяем размер с сохранением пропорций
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # Сохраняем миниатюру
            img.save(thumb_path, "JPEG", quality=85, optimize=True)
            return True
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return False


def save_product_image(upload_file, product_id: int, filename: str) -> Tuple[str, str]:
    """Сохранить изображение товара и создать миниатюру"""
    # Создаем папки для товара
    product_dir = Path(MEDIA_ROOT) / "products" / str(product_id)
    product_dir.mkdir(parents=True, exist_ok=True)

    # Полные пути к файлам
    file_path = product_dir / filename
    thumb_path = product_dir / f"thumb_{filename}"

    # Сохраняем оригинальный файл
    with open(file_path, "wb") as buffer:
        buffer.write(upload_file.file.read())

    # Создаем миниатюру
    create_thumbnail(str(file_path), str(thumb_path))

    return str(file_path), str(thumb_path)


def delete_product_image(file_path: str, thumb_path: str) -> bool:
    """Удалить изображение товара и его миниатюру"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
        return True
    except Exception as e:
        print(f"Error deleting image: {e}")
        return False


def get_image_url(file_path: str) -> str:
    """Получить URL для изображения"""
    if not file_path:
        return ""

    # Убираем MEDIA_ROOT из пути и добавляем /media/
    relative_path = file_path.replace(str(MEDIA_ROOT), "")
    return f"/media{relative_path}"


def validate_image_file(file) -> bool:
    """Проверить, что файл является изображением"""
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    return file.content_type in allowed_types


def get_file_extension(filename: str) -> str:
    """Получить расширение файла"""
    return Path(filename).suffix.lower()


def generate_unique_filename(product_id: int, original_filename: str) -> str:
    """Сгенерировать уникальное имя файла"""
    import secrets

    extension = get_file_extension(original_filename)
    unique_id = secrets.token_hex(8)
    return f"{product_id}_{unique_id}{extension}"
