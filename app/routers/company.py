from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyOut
from app.crud import company as crud_company
from app.crud import photo as crud_photo
from app.core.auth import require_admin_role
from typing import List
from app.services.images import save_company_image, delete_company_image_files
from app.schemas.photo import PhotoOut

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("/", response_model=CompanyOut, dependencies=[Depends(require_admin_role)])
def create_company(
    company: CompanyCreate,
    db: Session = Depends(get_db),
):
    """Создать новую компанию (только для администраторов)"""
    # Проверка на дубликат имени
    existing = crud_company.get_company_by_name(db, company.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Company with the same name already exists",
        )
    try:
        return crud_company.create_company(db, company)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Company with the same name already exists",
        )


@router.get("/", response_model=List[CompanyOut])
def read_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список компаний (публичный доступ)"""
    return crud_company.get_companies(db, skip=skip, limit=limit)


@router.get("/{company_id}", response_model=CompanyOut)
def read_company(company_id: int, db: Session = Depends(get_db)):
    """Получить компанию по ID (публичный доступ)"""
    db_company = crud_company.get_company(db, company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company


@router.patch(
    "/{company_id}",
    response_model=CompanyOut,
    dependencies=[Depends(require_admin_role)],
)
def update_company(
    company_id: int,
    company: CompanyUpdate,
    db: Session = Depends(get_db),
):
    """Обновить компанию (только для администраторов)"""
    # Если обновляется имя, проверяем дубликаты
    update_data = company.dict(exclude_unset=True)
    if "name" in update_data:
        existing = crud_company.get_company_by_name(db, update_data["name"])
        if existing and existing.id != company_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Company with the same name already exists",
            )
    try:
        updated = crud_company.update_company(db, company_id, company)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Company with the same name already exists",
        )
    if not updated:
        raise HTTPException(status_code=404, detail="Company not found")
    return updated


@router.delete("/{company_id}", dependencies=[Depends(require_admin_role)])
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
):
    """Удалить компанию (только для администраторов)"""
    deleted = crud_company.delete_company(db, company_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"message": "Company deleted successfully"}


@router.post(
    "/{company_id}/photos",
    response_model=List[PhotoOut],
    dependencies=[Depends(require_admin_role)],
)
async def upload_company_photos(
    company_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """Загрузить одно или несколько фото для компании (администраторы)"""
    company_obj = crud_company.get_company(db, company_id)
    if not company_obj:
        raise HTTPException(status_code=404, detail="Company not found")

    saved: List[PhotoOut] = []
    for upload in files:
        filename, filepath, thumbpath = await save_company_image(company_id, upload)
        photo = crud_photo.create_photo(db, company_id, filename, filepath, thumbpath)
        saved.append(photo)
    return saved


@router.get("/{company_id}/photos", response_model=List[PhotoOut])
def list_company_photos(company_id: int, db: Session = Depends(get_db)):
    """Список фото компании (публичный доступ)"""
    company_obj = crud_company.get_company(db, company_id)
    if not company_obj:
        raise HTTPException(status_code=404, detail="Company not found")
    photos = crud_photo.list_company_photos(db, company_id)
    return photos


@router.delete(
    "/{company_id}/photos/{photo_id}", dependencies=[Depends(require_admin_role)]
)
def delete_company_photo(
    company_id: int,
    photo_id: int,
    db: Session = Depends(get_db),
):
    """Удалить фото компании (администраторы)"""
    company_obj = crud_company.get_company(db, company_id)
    if not company_obj:
        raise HTTPException(status_code=404, detail="Company not found")
    photo = crud_photo.get_photo(db, photo_id)
    if not photo or photo.company_id != company_id:
        raise HTTPException(status_code=404, detail="Photo not found")
    # Cleanup files then delete record
    delete_company_image_files(photo.filepath, photo.thumbpath)
    ok = crud_photo.delete_photo(db, photo_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Photo not found")
    return {"message": "Photo deleted"}
