from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.core.auth import require_admin_role
from app.crud import category as crud_category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryWithComputed
from app.models.category import Category

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=List[CategoryWithComputed])
def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    all_categories = db.query(Category).all()
    categories = all_categories[skip : skip + limit]

    return crud_category.enrich_categories_with_computed_fields(
        db, categories, include_children=False
    )


@router.get("/tree", response_model=List[CategoryWithComputed])
def get_category_tree(db: Session = Depends(get_db)):

    roots = db.query(Category).filter(Category.parent_id.is_(None)).all()
    return crud_category.enrich_categories_with_computed_fields(db, roots)


@router.get("/root", response_model=List[CategoryWithComputed])
def get_root_categories(db: Session = Depends(get_db)):
    """Получить корневые категории"""
    try:
        categories = crud_category.get_root_categories(db)
        return crud_category.enrich_categories_with_computed_fields(
            db, categories, include_children=False
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при получении корневых категорий",
        )


@router.get("/{category_id}", response_model=CategoryWithComputed)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Получить категорию по ID"""
    try:
        category = crud_category.get_category(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена"
            )
        return crud_category.enrich_category_with_computed_fields(db, category)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при получении категории",
        )


@router.get("/{category_id}/children", response_model=List[CategoryWithComputed])
def get_category_children(category_id: int, db: Session = Depends(get_db)):
    parent = crud_category.get_category(db, category_id)
    if not parent:
        raise HTTPException(status_code=404, detail="Родительская категория не найдена")
    children = crud_category.get_category_children(db, category_id)
    return crud_category.enrich_categories_with_computed_fields(db, children)


@router.post(
    "/", response_model=CategoryWithComputed, dependencies=[Depends(require_admin_role)]
)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Создать новую категорию (только для админов)"""
    try:
        created_category = crud_category.create_category(db, category)
        all_categories = db.query(Category).all()
        return crud_category.enrich_category_with_computed_fields(
            db, created_category, all_categories
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при создании категории",
        )


@router.put(
    "/{category_id}",
    response_model=CategoryWithComputed,
    dependencies=[Depends(require_admin_role)],
)
def update_category(
    category_id: int, category: CategoryUpdate, db: Session = Depends(get_db)
):
    """Обновить категорию (только для админов)"""
    try:
        # Сначала проверяем существование
        existing_category = crud_category.get_category(db, category_id)
        if not existing_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена"
            )

        updated_category = crud_category.update_category(db, category_id, category)
        if not updated_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена"
            )

        # Предзагружаем для оптимизации
        all_categories = db.query(Category).all()
        return crud_category.enrich_category_with_computed_fields(
            db, updated_category, all_categories
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при обновлении категории",
        )


@router.delete("/{category_id}", dependencies=[Depends(require_admin_role)])
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    """Удалить категорию (только для админов)"""
    try:
        success = crud_category.delete_category(db, category_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена"
            )
        return {"message": "Категория успешно удалена"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при удалении категории",
        )
