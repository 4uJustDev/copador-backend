from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from typing import Optional, List


def get_product(db: Session, product_id: int) -> Optional[Product]:
    """Получить товар по ID"""
    try:
        return db.query(Product).filter(Product.id == product_id).first()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    """Получить список товаров с пагинацией"""
    try:
        return db.query(Product).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_product_by_sku(db: Session, sku: str) -> Optional[Product]:
    """Получить товар по SKU"""
    try:
        return db.query(Product).filter(Product.sku == sku).first()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_products_by_category(
    db: Session, category_id: int, skip: int = 0, limit: int = 100
) -> List[Product]:
    """Получить товары по категории"""
    try:
        return (
            db.query(Product)
            .filter(Product.category_id == category_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def search_products(
    db: Session, query: str, skip: int = 0, limit: int = 100
) -> List[Product]:
    """Поиск товаров по названию или описанию"""
    try:
        search_term = f"%{query}%"
        return (
            db.query(Product)
            .filter(
                (Product.name.ilike(search_term))
                | (Product.description.ilike(search_term))
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def create_product(db: Session, product: ProductCreate) -> Product:
    """Создать новый товар"""
    try:
        db_product = Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def update_product(
    db: Session, product_id: int, product: ProductUpdate
) -> Optional[Product]:
    """Обновить товар"""
    try:
        db_product = get_product(db, product_id)
        if not db_product:
            return None

        update_data = product.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)

        db.commit()
        db.refresh(db_product)
        return db_product
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def delete_product(db: Session, product_id: int) -> bool:
    """Удалить товар"""
    try:
        db_product = get_product(db, product_id)
        if db_product:
            db.delete(db_product)
            db.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def update_product_stock(
    db: Session, product_id: int, amount: int
) -> Optional[Product]:
    """Обновить количество товара на складе"""
    try:
        db_product = get_product(db, product_id)
        if not db_product:
            return None

        db_product.amount = amount
        db.commit()
        db.refresh(db_product)
        return db_product
    except SQLAlchemyError as e:
        db.rollback()
        raise e
