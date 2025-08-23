from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from typing import Optional, List


def get_category(db: Session, category_id: int) -> Optional[Category]:
    """Получить категорию по ID"""
    try:
        return db.query(Category).filter(Category.id == category_id).first()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
    """Получить список всех категорий с пагинацией"""
    try:
        return db.query(Category).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_root_categories(db: Session) -> List[Category]:
    """Получить корневые категории (без родителя)"""
    try:
        return db.query(Category).filter(Category.parent_id.is_(None)).all()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_category_by_sysname(db: Session, sysname: str) -> Optional[Category]:
    """Получить категорию по sysname"""
    try:
        return db.query(Category).filter(Category.sysname == sysname).first()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_category_children(db: Session, category_id: int) -> List[Category]:
    """Получить дочерние категории"""
    try:
        return db.query(Category).filter(Category.parent_id == category_id).all()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def create_category(db: Session, category: CategoryCreate) -> Category:
    """Создать новую категорию"""
    try:
        db_category = Category(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def update_category(
    db: Session, category_id: int, category: CategoryUpdate
) -> Optional[Category]:
    """Обновить категорию"""
    try:
        db_category = get_category(db, category_id)
        if not db_category:
            return None

        update_data = category.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)

        db.commit()
        db.refresh(db_category)
        return db_category
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def delete_category(db: Session, category_id: int) -> bool:
    """Удалить категорию"""
    try:
        db_category = get_category(db, category_id)
        if db_category:
            db.delete(db_category)
            db.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_category_tree(db: Session) -> List[Category]:
    """Получить полное дерево категорий"""
    try:
        # Получаем все категории и строим дерево
        all_categories = db.query(Category).all()
        category_dict = {cat.id: cat for cat in all_categories}

        # Строим дерево
        for category in all_categories:
            if category.parent_id and category.parent_id in category_dict:
                parent = category_dict[category.parent_id]
                parent.children.append(category)

        # Возвращаем только корневые категории
        return [cat for cat in all_categories if cat.parent_id is None]
    except SQLAlchemyError as e:
        db.rollback()
        raise e
