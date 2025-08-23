from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.core.auth import require_admin_role
from app.crud import category as crud_category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=List[CategoryOut])
def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Получить список всех категорий"""
    categories = crud_category.get_categories(db, skip=skip, limit=limit)
    return categories


@router.get("/tree", response_model=List[CategoryOut])
def get_category_tree(db: Session = Depends(get_db)):
    """Получить полное дерево категорий"""
    categories = crud_category.get_category_tree(db)
    return categories


@router.get("/root", response_model=List[CategoryOut])
def get_root_categories(db: Session = Depends(get_db)):
    """Получить корневые категории"""
    categories = crud_category.get_root_categories(db)
    return categories


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Получить категорию по ID"""
    category = crud_category.get_category(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return category


@router.get("/by-sysname/{sysname}", response_model=CategoryOut)
def get_category_by_sysname(sysname: str, db: Session = Depends(get_db)):
    """Получить категорию по sysname"""
    category = crud_category.get_category_by_sysname(db, sysname)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return category


@router.get("/{category_id}/children", response_model=List[CategoryOut])
def get_category_children(category_id: int, db: Session = Depends(get_db)):
    """Получить дочерние категории"""
    children = crud_category.get_category_children(db, category_id)
    return children


@router.post("/", response_model=CategoryOut)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin_role),
):
    """Создать новую категорию (только для админов)"""
    try:
        return crud_category.create_category(db, category)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin_role),
):
    """Обновить категорию (только для админов)"""
    updated_category = crud_category.update_category(db, category_id, category)
    if not updated_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return updated_category


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin_role),
):
    """Удалить категорию (только для админов)"""
    success = crud_category.delete_category(db, category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return {"message": "Category deleted successfully"}
