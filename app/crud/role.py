from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.role import Role
from app.models.user import UserRole
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
        db_role = Role(**role.model_dump())
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

        update_data = role.model_dump(exclude_unset=True)
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


# Функции для работы с пользовательскими ролями
def get_user_roles(db: Session, user_id: int) -> List[Role]:
    """Получить все роли пользователя"""
    try:
        return db.query(Role).join(UserRole).filter(UserRole.user_id == user_id).all()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def add_role_to_user(db: Session, user_id: int, role_id: int) -> bool:
    """Добавить роль пользователю"""
    try:
        # Проверяем, что роль уже не назначена
        existing = (
            db.query(UserRole)
            .filter(UserRole.user_id == user_id, UserRole.role_id == role_id)
            .first()
        )

        if existing:
            return True  # Роль уже назначена

        user_role = UserRole(user_id=user_id, role_id=role_id)
        db.add(user_role)
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        return False
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def remove_role_from_user(db: Session, user_id: int, role_id: int) -> bool:
    """Удалить роль у пользователя"""
    try:
        user_role = (
            db.query(UserRole)
            .filter(UserRole.user_id == user_id, UserRole.role_id == role_id)
            .first()
        )

        if user_role:
            db.delete(user_role)
            db.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def set_user_roles(db: Session, user_id: int, role_ids: List[int]) -> bool:
    """Установить роли пользователя (заменить существующие)"""
    try:
        # Удаляем все существующие роли
        db.query(UserRole).filter(UserRole.user_id == user_id).delete()

        # Добавляем новые роли
        for role_id in role_ids:
            user_role = UserRole(user_id=user_id, role_id=role_id)
            db.add(user_role)

        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise e
