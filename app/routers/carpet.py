from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.core.auth import require_admin_role
from app.crud import carpet as crud_carpet
from app.schemas.carpet import CarpetCreate, CarpetUpdate, CarpetOut, CarpetWithProduct

router = APIRouter(prefix="/carpets", tags=["Carpets"])


@router.get("/", response_model=List[CarpetOut])
def get_carpets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Получить список всех ковров"""
    carpets = crud_carpet.get_carpets(db, skip=skip, limit=limit)
    return carpets


@router.get("/search/material", response_model=List[CarpetOut])
def search_carpets_by_material(
    material: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Поиск ковров по материалу"""
    carpets = crud_carpet.search_carpets_by_material(
        db, material, skip=skip, limit=limit
    )
    return carpets


@router.get("/search/origin", response_model=List[CarpetOut])
def search_carpets_by_origin(
    origin: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Поиск ковров по происхождению"""
    carpets = crud_carpet.search_carpets_by_origin(db, origin, skip=skip, limit=limit)
    return carpets


@router.get("/search/size", response_model=List[CarpetOut])
def search_carpets_by_size(
    min_width: Optional[float] = Query(None, ge=0),
    max_width: Optional[float] = Query(None, ge=0),
    min_length: Optional[float] = Query(None, ge=0),
    max_length: Optional[float] = Query(None, ge=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Поиск ковров по размеру"""
    carpets = crud_carpet.get_carpets_by_size_range(
        db, min_width, max_width, min_length, max_length, skip, limit
    )
    return carpets


@router.get("/{carpet_id}", response_model=CarpetOut)
def get_carpet(carpet_id: int, db: Session = Depends(get_db)):
    """Получить ковер по ID"""
    carpet = crud_carpet.get_carpet(db, carpet_id)
    if not carpet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Carpet not found"
        )
    return carpet


@router.get("/product/{product_id}", response_model=CarpetOut)
def get_carpet_by_product_id(product_id: int, db: Session = Depends(get_db)):
    """Получить ковер по ID товара"""
    carpet = crud_carpet.get_carpet_by_product_id(db, product_id)
    if not carpet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Carpet not found"
        )
    return carpet


@router.post("/", response_model=CarpetOut, dependencies=[Depends(require_admin_role)])
def create_carpet(
    carpet: CarpetCreate,
    db: Session = Depends(get_db),
):
    """Создать новый ковер (только для админов)"""
    try:
        return crud_carpet.create_carpet(db, carpet)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/{carpet_id}", response_model=CarpetOut, dependencies=[Depends(require_admin_role)]
)
def update_carpet(
    carpet_id: int,
    carpet: CarpetUpdate,
    db: Session = Depends(get_db),
):
    """Обновить ковер (только для админов)"""
    updated_carpet = crud_carpet.update_carpet(db, carpet_id, carpet)
    if not updated_carpet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Carpet not found"
        )
    return updated_carpet


@router.delete("/{carpet_id}", dependencies=[Depends(require_admin_role)])
def delete_carpet(
    carpet_id: int,
    db: Session = Depends(get_db),
):
    """Удалить ковер (только для админов)"""
    success = crud_carpet.delete_carpet(db, carpet_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Carpet not found"
        )
    return {"message": "Carpet deleted successfully"}
