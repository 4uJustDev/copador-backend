from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryWithComputed
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


def is_category_leaf(db: Session, category_id: int) -> bool:
    """Проверить, является ли категория листом (не имеет дочерних элементов)"""
    try:
        children_count = (
            db.query(Category).filter(Category.parent_id == category_id).count()
        )
        return children_count == 0
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def create_category(db: Session, category: CategoryCreate) -> Category:
    """Создать новую категорию"""
    try:
        # Проверяем, что parent_id существует, если указан
        if category.parent_id is not None:
            parent = get_category(db, category.parent_id)
            if not parent:
                raise ValueError("Родительская категория не найдена")

        # Создаем категорию (без is_leaf - он вычисляется динамически)
        db_category = Category(
            name=category.name,
            sysname=category.sysname,
            parent_id=category.parent_id,
        )
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

        # Проверяем новый parent_id, если он указан
        if "parent_id" in update_data:
            new_parent_id = update_data["parent_id"]
            if new_parent_id is not None:
                parent = get_category(db, new_parent_id)
                if not parent:
                    raise ValueError("Родительская категория не найдена")
                if new_parent_id == category_id:
                    raise ValueError("Категория не может быть родителем самой себя")

        # Обновляем поля
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
        if not db_category:
            return False

        # Удаляем категорию (каскадное удаление дочерних элементов настроено в модели)
        db.delete(db_category)
        db.commit()

        return True
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


def enrich_category_with_computed_fields(
    db: Session, category: Category
) -> CategoryWithComputed:
    """Обогатить категорию вычисляемыми полями"""
    # Получаем дочерние элементы
    children = get_category_children(db, category.id)

    # Проверяем, является ли листом
    is_leaf = len(children) == 0

    # Создаем объект с вычисляемыми полями
    category_dict = {
        "id": category.id,
        "name": category.name,
        "sysname": category.sysname,
        "parent_id": category.parent_id,
        "created_at": category.created_at,
        "updated_at": category.updated_at,
        "_is_leaf": is_leaf,
        "_children": [
            enrich_category_with_computed_fields(db, child) for child in children
        ],
    }

    return CategoryWithComputed(**category_dict)


def enrich_categories_with_computed_fields(
    db: Session, categories: List[Category]
) -> List[CategoryWithComputed]:
    """Обогатить список категорий вычисляемыми полями"""
    return [enrich_category_with_computed_fields(db, cat) for cat in categories]
