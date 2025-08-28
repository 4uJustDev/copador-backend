from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.product_photo import ProductPhoto


def get_photos_by_product(db: Session, product_id: int) -> List[ProductPhoto]:
    return (
        db.query(ProductPhoto)
        .filter(ProductPhoto.product_id == product_id)
        .order_by(ProductPhoto.sort_order)
        .all()
    )


def get_photo(
    db: Session, photo_id: int, product_id: Optional[int] = None
) -> Optional[ProductPhoto]:
    query = db.query(ProductPhoto).filter(ProductPhoto.id == photo_id)
    if product_id is not None:
        query = query.filter(ProductPhoto.product_id == product_id)
    return query.first()


def create_photo(
    db: Session,
    *,
    product_id: int,
    filename: str,
    filepath: str,
    thumbpath: str,
    is_main: bool = False,
    sort_order: int = 0,
) -> ProductPhoto:
    if is_main:
        db.query(ProductPhoto).filter(
            ProductPhoto.product_id == product_id, ProductPhoto.is_main == True
        ).update({"is_main": False})

    photo = ProductPhoto(
        product_id=product_id,
        filename=filename,
        filepath=filepath,
        thumbpath=thumbpath,
        is_main=is_main,
        sort_order=sort_order,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def update_photo(
    db: Session,
    photo: ProductPhoto,
    *,
    is_main: Optional[bool] = None,
    sort_order: Optional[int] = None,
) -> ProductPhoto:
    if is_main:
        db.query(ProductPhoto).filter(
            ProductPhoto.product_id == photo.product_id,
            ProductPhoto.is_main == True,
            ProductPhoto.id != photo.id,
        ).update({"is_main": False})

    if is_main is not None:
        photo.is_main = is_main
    if sort_order is not None:
        photo.sort_order = sort_order

    db.commit()
    db.refresh(photo)
    return photo


def delete_photo(db: Session, photo: ProductPhoto) -> None:
    db.delete(photo)
    db.commit()


def reorder_photos(db: Session, product_id: int, photo_ids: List[int]) -> None:
    for index, photo_id in enumerate(photo_ids):
        p = (
            db.query(ProductPhoto)
            .filter(ProductPhoto.id == photo_id, ProductPhoto.product_id == product_id)
            .first()
        )
        if p:
            p.sort_order = index
    db.commit()
