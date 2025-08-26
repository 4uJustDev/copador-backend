from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.core.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user_dep,
)
from app.models.user import User, UserProfile
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.crud import role as crud_role

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Регистрация нового пользователя (создается с ролью customer по умолчанию)"""
    # Проверка существования пользователя
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )

    # Получаем роль customer по умолчанию
    customer_role = crud_role.get_role_by_name(db, "customer")
    if not customer_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Роль по умолчанию 'customer' не найдена",
        )

    try:
        # Создаем пользователя
        new_user = User(
            email=data.email,
            password_hash=hash_password(data.password),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Создаем профиль пользователя
        if data.first_name or data.last_name:
            user_profile = UserProfile(
                user_id=new_user.id,
                first_name=data.first_name,
                last_name=data.last_name,
            )
            db.add(user_profile)

        # Добавляем роль по умолчанию
        crud_role.add_role_to_user(db, new_user.id, customer_role.id)

        db.commit()
        db.refresh(new_user)

        # Создаем токен с user_id и массивом ролей
        token = create_access_token(
            {"user_id": new_user.id, "roles": new_user.role_names}
        )
        return {"access_token": token}
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Регистрация не удалась: нарушение целостности данных",
        )
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при регистрации",
        )


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Аутентификация пользователя"""
    try:
        user = db.query(User).filter(User.email == data.email).first()
        # Нет пользователя или пароль не установлен (например, соц. вход)
        if not user or not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
            )
        try:
            is_valid = verify_password(data.password, user.password_hash)
        except Exception:
            # Любые ошибки верификации отображаем как неуспешные креды, без раскрытия деталей
            is_valid = False
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
            )

        # Создаем токен с user_id и массивом ролей
        token = create_access_token({"user_id": user.id, "roles": user.role_names})
        return {"access_token": token}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при аутентификации",
        )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user_dep)):
    """Получить информацию о текущем пользователе"""
    try:
        return current_user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при получении профиля",
        )
