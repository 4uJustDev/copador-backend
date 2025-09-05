from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud import product_type as crud_product_type
from app.schemas.product_type import (
    ProductTypeCreate,
    ProductTypeUpdate,
    ProductTypeOut,
)
from app.core.auth import require_admin_role

router = APIRouter(prefix="/product-types", tags=["product-types"])


@router.post(
    "",
    response_model=ProductTypeOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_role)],
)
def create_product_type(product_type: ProductTypeCreate, db: Session = Depends(get_db)):
    """Создать новый тип товара"""
    try:
        return crud_product_type.create_product_type(db=db, product_type=product_type)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}",
        )


@router.get("", response_model=List[ProductTypeOut])
def read_product_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список типов товаров"""
    try:
        product_types = crud_product_type.get_product_types(db, skip=skip, limit=limit)
        return product_types
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении типов товаров: {str(e)}",
        )


@router.get("/{product_type_id}", response_model=ProductTypeOut)
def read_product_type(product_type_id: int, db: Session = Depends(get_db)):
    """Получить тип товара по ID"""
    try:
        product_type = crud_product_type.get_product_type(
            db, product_type_id=product_type_id
        )
        if product_type is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Тип товара с ID {product_type_id} не найден",
            )
        return product_type
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении типа товара: {str(e)}",
        )


@router.get("/by-sysname/{sysname}", response_model=ProductTypeOut)
def read_product_type_by_sysname(sysname: str, db: Session = Depends(get_db)):
    """Получить тип товара по sysname"""
    try:
        product_type = crud_product_type.get_product_type_by_sysname(
            db, sysname=sysname
        )
        if product_type is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Тип товара с sysname '{sysname}' не найден",
            )
        return product_type
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении типа товара: {str(e)}",
        )


@router.put(
    "/{product_type_id}",
    response_model=ProductTypeOut,
    dependencies=[Depends(require_admin_role)],
)
def update_product_type(
    product_type_id: int,
    product_type: ProductTypeUpdate,
    db: Session = Depends(get_db),
):
    """Обновить тип товара"""
    try:
        db_product_type = crud_product_type.update_product_type(
            db, product_type_id=product_type_id, product_type=product_type
        )
        if db_product_type is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Тип товара с ID {product_type_id} не найден",
            )
        return db_product_type
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении типа товара: {str(e)}",
        )


@router.delete(
    "/{product_type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin_role)],
)
def delete_product_type(product_type_id: int, db: Session = Depends(get_db)):
    """Удалить тип товара"""
    try:
        success = crud_product_type.delete_product_type(
            db, product_type_id=product_type_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Тип товара с ID {product_type_id} не найден",
            )
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении типа товара: {str(e)}",
        )
