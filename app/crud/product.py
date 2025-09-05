from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from typing import Optional, List


def get_product(db: Session, product_id: int) -> Optional[Product]:
    """Получить товар по ID с фотографиями"""
    try:
        return (
            db.query(Product)
            .options(joinedload(Product.photos))
            .filter(Product.id == product_id)
            .first()
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    """Получить список товаров с пагинацией и фотографиями"""
    try:
        return (
            db.query(Product)
            .options(joinedload(Product.photos))
            .offset(skip)
            .limit(limit)
            .all()
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_product_by_sku(db: Session, sku: str) -> Optional[Product]:
    """Получить товар по SKU с фотографиями"""
    try:
        return (
            db.query(Product)
            .options(joinedload(Product.photos))
            .filter(Product.sku == sku)
            .first()
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_products_by_product_type_sysname_with_extended_info(
    db: Session, product_type_sysname: str, skip: int = 0, limit: int = 100
) -> List[Product]:
    """Получить товары по sysname типа товара с дополнительной информацией и фотографиями"""
    try:
        from app.models.category import Category
        from app.models.product_type import ProductType
        from app.models.carpet import Carpet
        from app.services.product_extensions import ProductExtensionService

        query = (
            db.query(Product)
            .options(joinedload(Product.photos))
            .join(Category, Product.category_id == Category.id)
            .join(ProductType, Category.product_type_id == ProductType.id)
            .filter(ProductType.sysname == product_type_sysname)
        )

        if product_type_sysname == "carpet":
            query = query.outerjoin(Carpet, Product.id == Carpet.product_id)

        products = query.offset(skip).limit(limit).all()

        for product in products:
            product.extended_info = ProductExtensionService.get_extended_info(
                product, product_type_sysname
            )

        return products
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_products_by_category_id_with_extended_info(
    db: Session, category_id: int, skip: int = 0, limit: int = 100
) -> List[Product]:
    """Получить товары по ID категории (включая дочерние) с расширенной информацией и фото"""
    try:
        from app.models.category import Category
        from app.models.carpet import Carpet
        from app.services.product_extensions import ProductExtensionService

        # Собираем все ID дочерних категорий (включая родительскую)
        category_ids: List[int] = []
        queue: List[int] = [category_id]
        while queue:
            category_ids.extend(queue)
            children = db.query(Category.id).filter(Category.parent_id.in_(queue)).all()
            queue = [child_id for (child_id,) in children]

        if not category_ids:
            return []

        query = (
            db.query(Product)
            .options(
                joinedload(Product.photos),
                joinedload(Product.category).joinedload(Category.product_type),
            )
            .filter(Product.category_id.in_(category_ids))
            .outerjoin(Carpet, Product.id == Carpet.product_id)
        )

        products = query.offset(skip).limit(limit).all()

        for product in products:
            product_type_sysname = (
                product.category.product_type.sysname
                if product.category and product.category.product_type
                else None
            )
            product.extended_info = ProductExtensionService.get_extended_info(
                product, product_type_sysname
            )

        return products
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def search_products(
    db: Session, query: str, skip: int = 0, limit: int = 100
) -> List[Product]:
    """Поиск товаров по названию или описанию с фотографиями"""
    try:
        search_term = f"%{query}%"
        return (
            db.query(Product)
            .options(joinedload(Product.photos))
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
        existing_product = get_product_by_sku(db, product.sku)
        if existing_product:
            raise ValueError(f"Товар с SKU '{product.sku}' уже существует")

        if product.price < 0:
            raise ValueError("Цена товара не может быть отрицательной")

        if product.amount < 0:
            raise ValueError("Количество товара не может быть отрицательным")

        db_product = Product(**product.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)

        return get_product(db, db_product.id)
    except IntegrityError as e:
        db.rollback()
        if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
            raise ValueError(f"Товар с SKU '{product.sku}' уже существует")
        raise ValueError(f"Ошибка при создании товара: {str(e)}")
    except ValueError as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Ошибка базы данных при создании товара: {str(e)}")


def update_product(
    db: Session, product_id: int, product: ProductUpdate
) -> Optional[Product]:
    """Обновить товар"""
    try:
        db_product = get_product(db, product_id)
        if not db_product:
            return None

        update_data = product.model_dump(exclude_unset=True)

        if "sku" in update_data:
            existing_product = get_product_by_sku(db, update_data["sku"])
            if existing_product and existing_product.id != product_id:
                raise ValueError(f"Товар с SKU '{update_data['sku']}' уже существует")

        if "price" in update_data and update_data["price"] < 0:
            raise ValueError("Цена товара не может быть отрицательной")

        if "amount" in update_data and update_data["amount"] < 0:
            raise ValueError("Количество товара не может быть отрицательным")

        for field, value in update_data.items():
            setattr(db_product, field, value)

        db.commit()
        db.refresh(db_product)

        return get_product(db, product_id)
    except IntegrityError as e:
        db.rollback()
        if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
            raise ValueError(f"Товар с таким SKU уже существует")
        raise ValueError(f"Ошибка при обновлении товара: {str(e)}")
    except ValueError as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Ошибка базы данных при обновлении товара: {str(e)}")


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
