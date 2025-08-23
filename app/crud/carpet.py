from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.carpet import Carpet
from app.schemas.carpet import CarpetCreate, CarpetUpdate
from typing import Optional, List


def get_carpet(db: Session, carpet_id: int) -> Optional[Carpet]:
    """Получить ковер по ID"""
    try:
        return db.query(Carpet).filter(Carpet.id == carpet_id).first()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_carpet_by_product_id(db: Session, product_id: int) -> Optional[Carpet]:
    """Получить ковер по ID товара"""
    try:
        return db.query(Carpet).filter(Carpet.product_id == product_id).first()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_carpets(db: Session, skip: int = 0, limit: int = 100) -> List[Carpet]:
    """Получить список ковров с пагинацией"""
    try:
        return db.query(Carpet).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def search_carpets_by_material(
    db: Session, material: str, skip: int = 0, limit: int = 100
) -> List[Carpet]:
    """Поиск ковров по материалу"""
    try:
        return (
            db.query(Carpet)
            .filter(Carpet.material.ilike(f"%{material}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def search_carpets_by_origin(
    db: Session, origin: str, skip: int = 0, limit: int = 100
) -> List[Carpet]:
    """Поиск ковров по происхождению"""
    try:
        return (
            db.query(Carpet)
            .filter(Carpet.origin.ilike(f"%{origin}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def create_carpet(db: Session, carpet: CarpetCreate) -> Carpet:
    """Создать новый ковер"""
    try:
        db_carpet = Carpet(**carpet.dict())
        db.add(db_carpet)
        db.commit()
        db.refresh(db_carpet)
        return db_carpet
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def update_carpet(
    db: Session, carpet_id: int, carpet: CarpetUpdate
) -> Optional[Carpet]:
    """Обновить ковер"""
    try:
        db_carpet = get_carpet(db, carpet_id)
        if not db_carpet:
            return None

        update_data = carpet.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_carpet, field, value)

        db.commit()
        db.refresh(db_carpet)
        return db_carpet
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def delete_carpet(db: Session, carpet_id: int) -> bool:
    """Удалить ковер"""
    try:
        db_carpet = get_carpet(db, carpet_id)
        if db_carpet:
            db.delete(db_carpet)
            db.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_carpets_by_size_range(
    db: Session,
    min_width: float = None,
    max_width: float = None,
    min_length: float = None,
    max_length: float = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Carpet]:
    """Поиск ковров по диапазону размеров"""
    try:
        query = db.query(Carpet)

        if min_width is not None:
            query = query.filter(Carpet.width >= min_width)
        if max_width is not None:
            query = query.filter(Carpet.width <= max_width)
        if min_length is not None:
            query = query.filter(Carpet.length >= min_length)
        if max_length is not None:
            query = query.filter(Carpet.length <= max_length)

        return query.offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        db.rollback()
        raise e
