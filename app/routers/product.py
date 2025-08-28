from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query,
    UploadFile,
    File,
    Form,
)
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.core.auth import require_admin_role
from app.crud import product as crud_product
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductOut,
    ProductWithPhotos,
)
from app.schemas.product_photo import ProductPhotoUpdate, ProductPhotoOut
from app.models.product_photo import ProductPhoto
from app.services.images import (
    save_product_image,
    delete_product_image,
    validate_image_file,
    generate_unique_filename,
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=List[ProductOut])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Получить список всех товаров"""
    products = crud_product.get_products(db, skip=skip, limit=limit)
    return products


@router.get("/search", response_model=List[ProductOut])
def search_products(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Поиск товаров по названию или описанию"""
    products = crud_product.search_products(db, q, skip=skip, limit=limit)
    return products


@router.get("/category/{category_id}", response_model=List[ProductOut])
def get_products_by_category(
    category_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Получить товары по категории"""
    products = crud_product.get_products_by_category(
        db, category_id, skip=skip, limit=limit
    )
    return products


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Получить товар по ID"""
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return product


@router.get("/{product_id}/with-photos", response_model=ProductWithPhotos)
def get_product_with_photos(product_id: int, db: Session = Depends(get_db)):
    """Получить товар с фотографиями"""
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return product


@router.get("/sku/{sku}", response_model=ProductOut)
def get_product_by_sku(sku: str, db: Session = Depends(get_db)):
    """Получить товар по SKU"""
    product = crud_product.get_product_by_sku(db, sku)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return product


@router.post(
    "/",
    response_model=ProductOut,
    dependencies=[Depends(require_admin_role)],
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
):
    """Создать новый товар (только для админов)"""
    try:
        return crud_product.create_product(db, product)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/{product_id}",
    response_model=ProductOut,
    dependencies=[Depends(require_admin_role)],
)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
):
    """Обновить товар (только для админов)"""
    updated_product = crud_product.update_product(db, product_id, product)
    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return updated_product


@router.delete(
    "/{product_id}",
    dependencies=[Depends(require_admin_role)],
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Удалить товар (только для админов)"""
    success = crud_product.delete_product(db, product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return {"message": "Product deleted successfully"}


# ===== ФОТОГРАФИИ ТОВАРОВ =====


@router.get("/{product_id}/photos", response_model=List[ProductPhotoOut])
def get_product_photos(product_id: int, db: Session = Depends(get_db)):
    """Получить все фотографии товара"""
    # Проверяем, что товар существует
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    photos = (
        db.query(ProductPhoto)
        .filter(ProductPhoto.product_id == product_id)
        .order_by(ProductPhoto.sort_order)
        .all()
    )
    return photos


@router.post(
    "/{product_id}/photos",
    dependencies=[Depends(require_admin_role)],
)
async def upload_product_photo(
    product_id: int,
    file: UploadFile = File(...),
    is_main: bool = Form(False),
    sort_order: int = Form(0),
    db: Session = Depends(get_db),
):
    """Загрузить фотографию для товара (только для админов)"""
    # Проверяем, что товар существует
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    # Проверяем тип файла
    if not validate_image_file(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image (JPEG, PNG, WebP)",
        )

    # Генерируем уникальное имя файла
    filename = generate_unique_filename(product_id, file.filename)

    try:
        # Сохраняем файл и создаем миниатюру
        file_path, thumb_path = save_product_image(file, product_id, filename)

        # Если это главное фото, снимаем флаг с других фото
        if is_main:
            db.query(ProductPhoto).filter(
                ProductPhoto.product_id == product_id, ProductPhoto.is_main == True
            ).update({"is_main": False})

        # Создаем запись в БД
        photo = ProductPhoto(
            product_id=product_id,
            filename=filename,
            filepath=file_path,
            thumbpath=thumb_path,
            is_main=is_main,
            sort_order=sort_order,
        )

        db.add(photo)
        db.commit()
        db.refresh(photo)

        return photo

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}",
        )


@router.get("/{product_id}/photos/{photo_id}", response_model=ProductPhotoOut)
def get_product_photo(product_id: int, photo_id: int, db: Session = Depends(get_db)):
    """Получить конкретную фотографию товара"""
    # Проверяем, что товар существует
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    photo = (
        db.query(ProductPhoto)
        .filter(ProductPhoto.id == photo_id, ProductPhoto.product_id == product_id)
        .first()
    )
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


@router.put(
    "/{product_id}/photos/{photo_id}",
    response_model=ProductPhotoOut,
    dependencies=[Depends(require_admin_role)],
)
def update_product_photo(
    product_id: int,
    photo_id: int,
    photo_update: ProductPhotoUpdate,
    db: Session = Depends(get_db),
):
    """Обновить информацию о фотографии (только для админов)"""
    # Проверяем, что товар существует
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    photo = (
        db.query(ProductPhoto)
        .filter(ProductPhoto.id == photo_id, ProductPhoto.product_id == product_id)
        .first()
    )
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )

    # Если устанавливаем как главное фото, снимаем флаг с других
    if photo_update.is_main:
        db.query(ProductPhoto).filter(
            ProductPhoto.product_id == photo.product_id,
            ProductPhoto.is_main == True,
            ProductPhoto.id != photo_id,
        ).update({"is_main": False})

    # Обновляем поля
    update_data = photo_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(photo, field, value)

    db.commit()
    db.refresh(photo)
    return photo


@router.delete(
    "/{product_id}/photos/{photo_id}",
    dependencies=[Depends(require_admin_role)],
)
def delete_product_photo(
    product_id: int,
    photo_id: int,
    db: Session = Depends(get_db),
):
    """Удалить фотографию (только для админов)"""
    # Проверяем, что товар существует
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    photo = (
        db.query(ProductPhoto)
        .filter(ProductPhoto.id == photo_id, ProductPhoto.product_id == product_id)
        .first()
    )
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )

    try:
        # Удаляем файлы с диска
        delete_product_image(photo.filepath, photo.thumbpath)

        # Удаляем запись из БД
        db.delete(photo)
        db.commit()

        return {"message": "Photo deleted successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete photo: {str(e)}",
        )


@router.post(
    "/{product_id}/photos/{photo_id}/set-main",
    dependencies=[Depends(require_admin_role)],
)
def set_main_photo(
    product_id: int,
    photo_id: int,
    db: Session = Depends(get_db),
):
    """Установить фотографию как главную (только для админов)"""
    # Проверяем, что товар существует
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    photo = (
        db.query(ProductPhoto)
        .filter(ProductPhoto.id == photo_id, ProductPhoto.product_id == product_id)
        .first()
    )
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )

    # Снимаем флаг главного фото с других фото этого товара
    db.query(ProductPhoto).filter(
        ProductPhoto.product_id == photo.product_id, ProductPhoto.is_main == True
    ).update({"is_main": False})

    # Устанавливаем флаг главного фото
    photo.is_main = True
    db.commit()

    return {"message": "Main photo set successfully"}


@router.post(
    "/{product_id}/photos/reorder",
    dependencies=[Depends(require_admin_role)],
)
def reorder_photos(
    product_id: int,
    photo_ids: List[int],
    db: Session = Depends(get_db),
):
    """Переупорядочить фотографии товара (только для админов)"""
    # Проверяем, что товар существует
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    for index, photo_id in enumerate(photo_ids):
        photo = (
            db.query(ProductPhoto)
            .filter(ProductPhoto.id == photo_id, ProductPhoto.product_id == product_id)
            .first()
        )
        if photo:
            photo.sort_order = index

    db.commit()
    return {"message": "Photos reordered successfully"}
