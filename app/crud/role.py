from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate
from typing import Optional, List


def get_role(db: Session, role_id: int) -> Optional[Role]:
    """Получить роль по ID"""
    try:
        return db.query(Role).filter(Role.id == role_id).first()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
    """Получить список ролей с пагинацией"""
    try:
        return db.query(Role).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    """Получить роль по названию"""
    try:
        return db.query(Role).filter(Role.name == name).first()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def create_role(db: Session, role: RoleCreate) -> Role:
    """Создать новую роль"""
    try:
        db_role = Role(**role.dict())
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def update_role(db: Session, role_id: int, role: RoleUpdate) -> Optional[Role]:
    """Обновить роль"""
    try:
        db_role = get_role(db, role_id)
        if not db_role:
            return None

        update_data = role.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_role, field, value)

        db.commit()
        db.refresh(db_role)
        return db_role
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def delete_role(db: Session, role_id: int) -> bool:
    """Удалить роль"""
    try:
        db_role = get_role(db, role_id)
        if db_role:
            db.delete(db_role)
            db.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.rollback()
        raise e
