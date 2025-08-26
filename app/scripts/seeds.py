#!/usr/bin/env python3
"""
Скрипт для инициализации базовых данных:
- Роли: admin, customer
- Админ-пользователь с ролью admin
"""

import sys
import os

from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.core.auth import hash_password
from app.crud import role as crud_role
from app.schemas.role import RoleCreate

admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
admin_password = os.getenv("ADMIN_PASSWORD")

if not admin_password:
    print("Переменная окружения ADMIN_PASSWORD обязательна")
    exit(1)


def seed_data(db: Session):
    """Инициализация базовых данных"""
    try:
        # Создаем роли, если их нет
        roles_data = [
            {"name": "admin", "description": "Администратор с полными правами доступа"},
            {"name": "customer", "description": "Покупатель (роль по умолчанию)"},
        ]

        created_roles = {}
        for role_data in roles_data:
            existing_role = crud_role.get_role_by_name(db, role_data["name"])
            if not existing_role:
                role = RoleCreate(**role_data)
                created_role = crud_role.create_role(db, role)
                created_roles[role_data["name"]] = created_role
                print(f"✅ Создана роль: {created_role.name} (ID: {created_role.id})")
            else:
                created_roles[role_data["name"]] = existing_role
                print(
                    f"ℹ️  Роль {existing_role.name} уже существует (ID: {existing_role.id})"
                )

        # Создаем админа, если его нет
        admin_role = created_roles.get("admin")
        if not admin_role:
            print("❌ Роль admin не найдена, создание админа пропущено")
            return

        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            admin_user = User(
                email=admin_email,
                password_hash=hash_password(admin_password),
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

            # Назначаем роль admin через таблицу UserRole
            db.add(UserRole(user_id=admin_user.id, role_id=admin_role.id))
            db.commit()
            print(f"✅ Создан админ пользователь: {admin_email} (Role: admin)")
        else:
            # Убеждаемся, что у пользователя есть роль admin
            has_admin = any(
                ur.role_id == admin_role.id for ur in existing_admin.user_roles
            )
            if not has_admin:
                db.add(UserRole(user_id=existing_admin.id, role_id=admin_role.id))
                db.commit()
                print(f"✅ Добавлена роль admin пользователю {admin_email}")
            else:
                print("ℹ️  Админ пользователь уже существует с ролью admin")

        print("🎉 Инициализация данных завершена успешно!")

    except Exception as e:
        print(f"❌ Ошибка при инициализации данных: {e}")
        db.rollback()
        raise


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()
