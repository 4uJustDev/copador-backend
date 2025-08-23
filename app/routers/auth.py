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
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
        )

    # Получаем роль customer по умолчанию
    customer_role = crud_role.get_role_by_name(db, "customer")
    if not customer_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default customer role not found",
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
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Аутентификация пользователя"""
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    # Создаем токен с user_id и массивом ролей
    token = create_access_token({"user_id": user.id, "roles": user.role_names})
    return {"access_token": token}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user_dep)):
    """Получить информацию о текущем пользователе"""
    return current_user
