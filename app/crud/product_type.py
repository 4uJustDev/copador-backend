from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.product_type import ProductType
from app.schemas.product_type import ProductTypeCreate, ProductTypeUpdate
from typing import Optional, List


def get_product_type(db: Session, product_type_id: int) -> Optional[ProductType]:
    """Получить тип товара по ID"""
    try:
        return db.query(ProductType).filter(ProductType.id == product_type_id).first()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_product_type_by_sysname(db: Session, sysname: str) -> Optional[ProductType]:
    """Получить тип товара по sysname"""
    try:
        return db.query(ProductType).filter(ProductType.sysname == sysname).first()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_product_types(
    db: Session, skip: int = 0, limit: int = 100
) -> List[ProductType]:
    """Получить список типов товаров"""
    try:
        return db.query(ProductType).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def create_product_type(db: Session, product_type: ProductTypeCreate) -> ProductType:
    """Создать новый тип товара"""
    try:
        # Проверяем, не существует ли уже тип товара с таким sysname
        existing_product_type = get_product_type_by_sysname(db, product_type.sysname)
        if existing_product_type:
            raise ValueError(
                f"Тип товара с sysname '{product_type.sysname}' уже существует"
            )

        db_product_type = ProductType(**product_type.model_dump())
        db.add(db_product_type)
        db.commit()
        db.refresh(db_product_type)
        return db_product_type
    except IntegrityError as e:
        db.rollback()
        if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
            raise ValueError(
                f"Тип товара с sysname '{product_type.sysname}' уже существует"
            )
        raise ValueError(f"Ошибка при создании типа товара: {str(e)}")
    except ValueError as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Ошибка базы данных при создании типа товара: {str(e)}")


def update_product_type(
    db: Session, product_type_id: int, product_type: ProductTypeUpdate
) -> Optional[ProductType]:
    """Обновить тип товара"""
    try:
        db_product_type = get_product_type(db, product_type_id)
        if not db_product_type:
            return None

        update_data = product_type.model_dump(exclude_unset=True)

        # Проверяем, не конфликтует ли новый sysname с существующим
        if "sysname" in update_data:
            existing_product_type = get_product_type_by_sysname(
                db, update_data["sysname"]
            )
            if existing_product_type and existing_product_type.id != product_type_id:
                raise ValueError(
                    f"Тип товара с sysname '{update_data['sysname']}' уже существует"
                )

        for field, value in update_data.items():
            setattr(db_product_type, field, value)

        db.commit()
        db.refresh(db_product_type)
        return db_product_type
    except IntegrityError as e:
        db.rollback()
        if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
            raise ValueError(f"Тип товара с таким sysname уже существует")
        raise ValueError(f"Ошибка при обновлении типа товара: {str(e)}")
    except ValueError as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Ошибка базы данных при обновлении типа товара: {str(e)}")


def delete_product_type(db: Session, product_type_id: int) -> bool:
    """Удалить тип товара"""
    try:
        db_product_type = get_product_type(db, product_type_id)
        if not db_product_type:
            return False

        # Проверяем, есть ли связанные категории
        if db_product_type.categories:
            raise ValueError(
                f"Нельзя удалить тип товара '{db_product_type.name}', так как он связан с категориями"
            )

        db.delete(db_product_type)
        db.commit()
        return True
    except ValueError as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Ошибка базы данных при удалении типа товара: {str(e)}")
