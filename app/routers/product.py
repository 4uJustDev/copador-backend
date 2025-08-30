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
from typing import List, Optional
from app.database import get_db
from app.core.auth import require_admin_role
from app.crud import product as crud_product
from app.crud import photo as crud_photo
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductOut,
    ProductWithExtendedInfo,
)
from app.schemas.product_photo import (
    ProductPhotoUpdate,
    ProductPhotoOut,
    PhotoReorderRequest,
)
from app.services.images import (
    save_product_image,
    delete_product_image,
    validate_image_file,
    generate_unique_filename,
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=List[ProductWithExtendedInfo])
def read_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category_sysname: Optional[str] = Query(
        None, description="Фильтр по типу товара (sysname категории)"
    ),
    db: Session = Depends(get_db),
):
    """Получить список всех товаров или с дополнительной информацией"""
    try:
        if category_sysname:
            products = crud_product.get_products_by_category_sysname_with_extended_info(
                db, category_sysname, skip=skip, limit=limit
            )
        else:
            products = crud_product.get_products(db, skip=skip, limit=limit)
        return products
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении товаров: {str(e)}",
        )


@router.get("/search", response_model=List[ProductOut])
def search_products(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Поиск товаров по названию или описанию"""
    try:
        products = crud_product.search_products(db, q, skip=skip, limit=limit)
        return products
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при поиске товаров: {str(e)}",
        )


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Получить товар по ID"""
    try:
        product = crud_product.get_product(db, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Товар с ID {product_id} не найден",
            )
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении товара: {str(e)}",
        )


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
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}",
        )


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
    try:
        updated_product = crud_product.update_product(db, product_id, product)
        if not updated_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Товар с ID {product_id} не найден",
            )
        return updated_product
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении товара: {str(e)}",
        )


@router.delete(
    "/{product_id}",
    dependencies=[Depends(require_admin_role)],
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Удалить товар (только для админов)"""
    try:
        success = crud_product.delete_product(db, product_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Товар с ID {product_id} не найден",
            )
        return {"message": "Товар успешно удален"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении товара: {str(e)}",
        )


# ===== ФОТОГРАФИИ ТОВАРОВ =====


@router.get("/{product_id}/photos", response_model=List[ProductPhotoOut])
def get_product_photos(product_id: int, db: Session = Depends(get_db)):
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return crud_photo.get_photos_by_product(db, product_id)


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
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    if not validate_image_file(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image (JPEG, PNG, WebP)",
        )

    filename = generate_unique_filename(product_id, file.filename)
    try:
        file_path, thumb_path = save_product_image(file, product_id, filename)
        photo = crud_photo.create_photo(
            db,
            product_id=product_id,
            filename=filename,
            filepath=file_path,
            thumbpath=thumb_path,
            is_main=is_main,
            sort_order=sort_order,
        )
        return photo
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}",
        )


@router.get("/{product_id}/photos/{photo_id}", response_model=ProductPhotoOut)
def get_product_photo(product_id: int, photo_id: int, db: Session = Depends(get_db)):
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    photo = crud_photo.get_photo(db, photo_id, product_id)
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
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    photo = crud_photo.get_photo(db, photo_id, product_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )

    updated = crud_photo.update_photo(
        db,
        photo,
        is_main=photo_update.is_main,
        sort_order=photo_update.sort_order,
    )
    return updated


@router.delete(
    "/{product_id}/photos/{photo_id}",
    dependencies=[Depends(require_admin_role)],
)
def delete_product_photo(
    product_id: int,
    photo_id: int,
    db: Session = Depends(get_db),
):
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    photo = crud_photo.get_photo(db, photo_id, product_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )

    delete_product_image(photo.filepath, photo.thumbpath)
    crud_photo.delete_photo(db, photo)
    return {"message": "Photo deleted successfully"}


@router.post(
    "/{product_id}/photos/{photo_id}/set-main",
    dependencies=[Depends(require_admin_role)],
)
def set_main_photo(
    product_id: int,
    photo_id: int,
    db: Session = Depends(get_db),
):
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    photo = crud_photo.get_photo(db, photo_id, product_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )

    crud_photo.update_photo(db, photo, is_main=True)
    return {"message": "Main photo set successfully"}


@router.post(
    "/{product_id}/photos/reorder",
    dependencies=[Depends(require_admin_role)],
)
def reorder_photos(
    product_id: int,
    body: PhotoReorderRequest,
    db: Session = Depends(get_db),
):
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    crud_photo.reorder_photos(db, product_id, body.photo_ids)
    return {"message": "Photos reordered successfully"}
