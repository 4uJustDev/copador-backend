from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.schemas.role import RoleCreate, RoleUpdate, RoleOut
from app.crud import role as crud_role
from app.core.auth import require_admin_role
from app.models.user import User
from typing import List

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("/", response_model=RoleOut, dependencies=[Depends(require_admin_role)])
def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
):
    """Создать новую роль (только для администраторов)"""
    # Проверка на дубликат имени
    existing = crud_role.get_role_by_name(db, role.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role with the same name already exists",
        )
    try:
        return crud_role.create_role(db, role)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role with the same name already exists",
        )


@router.get("/", response_model=List[RoleOut])
def read_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список ролей (публичный доступ)"""
    return crud_role.get_roles(db, skip=skip, limit=limit)


@router.get("/{role_id}", response_model=RoleOut)
def read_role(role_id: int, db: Session = Depends(get_db)):
    """Получить роль по ID (публичный доступ)"""
    db_role = crud_role.get_role(db, role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role


@router.patch(
    "/{role_id}", response_model=RoleOut, dependencies=[Depends(require_admin_role)]
)
def update_role(
    role_id: int,
    role: RoleUpdate,
    db: Session = Depends(get_db),
):
    """Обновить роль (только для администраторов)"""
    # Если обновляется имя, проверяем дубликаты
    update_data = role.model_dump(exclude_unset=True)
    if "name" in update_data:
        existing = crud_role.get_role_by_name(db, update_data["name"])
        if existing and existing.id != role_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Role with the same name already exists",
            )
    try:
        updated = crud_role.update_role(db, role_id, role)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role with the same name already exists",
        )
    if not updated:
        raise HTTPException(status_code=404, detail="Role not found")
    return updated


@router.delete("/{role_id}", dependencies=[Depends(require_admin_role)])
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
):
    """Удалить роль (только для администраторов)"""
    deleted = crud_role.delete_role(db, role_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role deleted successfully"}
