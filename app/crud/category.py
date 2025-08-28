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
                # Проверка на циклы в иерархии
                current_parent_id = new_parent_id
                while current_parent_id is not None:
                    if current_parent_id == category_id:
                        raise ValueError(
                            "Обнаружена циклическая ссылка в иерархии категорий"
                        )
                    parent_category = get_category(db, current_parent_id)
                    current_parent_id = (
                        parent_category.parent_id if parent_category else None
                    )

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
    return db.query(Category).filter(Category.parent_id.is_(None)).all()


def _build_category_tree_node(category, category_dict):
    """Рекурсивно строит узел дерева"""
    node = {
        "id": category.id,
        "name": category.name,
        "sysname": category.sysname,
        "parent_id": category.parent_id,
        "created_at": category.created_at,
        "updated_at": category.updated_at,
        "children": [],
    }

    # Находим детей и рекурсивно строим для них дерево
    children = [cat for cat in category_dict.values() if cat.parent_id == category.id]
    for child in children:
        node["children"].append(_build_category_tree_node(child, category_dict))

    return node


def enrich_category_with_computed_fields(
    db: Session,
    category: Category,
    all_categories: List[Category] = None,
    include_children: bool = True,
) -> CategoryWithComputed:
    """Обогатить категорию вычисляемыми полями"""
    if all_categories is None:
        all_categories = db.query(Category).all()

    # Находим детей из предзагруженного списка
    children = [cat for cat in all_categories if cat.parent_id == category.id]
    is_leaf = len(children) == 0

    # Рекурсивно обогащаем детей, если это требуется
    if include_children:
        enriched_children = [
            enrich_category_with_computed_fields(
                db, child, all_categories, include_children
            )
            for child in children
        ]
    else:
        enriched_children = []

    return CategoryWithComputed(
        id=category.id,
        name=category.name,
        sysname=category.sysname,
        parent_id=category.parent_id,
        created_at=category.created_at,
        updated_at=category.updated_at,
        is_leaf=is_leaf,
        children=enriched_children,
    )


def enrich_categories_with_computed_fields(
    db: Session, categories: List[Category], include_children: bool = True
) -> List[CategoryWithComputed]:
    """Обогатить список категорий вычисляемыми полями"""
    return [
        enrich_category_with_computed_fields(
            db, cat, None, include_children=include_children
        )
        for cat in categories
    ]
