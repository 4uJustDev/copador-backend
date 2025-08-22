from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.photo import Photo


def create_photo(
    db: Session, company_id: int, filename: str, filepath: str, thumbpath: str
) -> Photo:
    photo = Photo(
        company_id=company_id, filename=filename, filepath=filepath, thumbpath=thumbpath
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def list_company_photos(db: Session, company_id: int) -> List[Photo]:
    return db.query(Photo).filter(Photo.company_id == company_id).all()


def get_photo(db: Session, photo_id: int) -> Optional[Photo]:
    return db.query(Photo).filter(Photo.id == photo_id).first()


def delete_photo(db: Session, photo_id: int) -> bool:
    photo = get_photo(db, photo_id)
    if not photo:
        return False
    db.delete(photo)
    db.commit()
    return True
