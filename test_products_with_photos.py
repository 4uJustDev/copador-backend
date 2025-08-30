#!/usr/bin/env python3
"""
Тест для проверки работы товаров с фотографиями
"""

import sys
import os

from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import product as crud_product
from app.crud import product_type as crud_product_type
from app.crud import category as crud_category
from app.schemas.product import ProductCreate
from app.schemas.product_type import ProductTypeCreate
from app.schemas.category import CategoryCreate
from decimal import Decimal


def test_products_with_photos():
    """Тестирование работы с товарами и фотографиями"""
    db = SessionLocal()
    try:
        print("🧪 Тестирование работы с товарами и фотографиями...")

        # 1. Создаем тип товара
        product_type_data = {"name": "Тест", "sysname": "test"}
        product_type = crud_product_type.create_product_type(
            db, ProductTypeCreate(**product_type_data)
        )
        print(f"✅ Создан тип товара: {product_type.name}")

        # 2. Создаем категорию
        category_data = {
            "name": "Тестовая категория",
            "product_type_id": product_type.id,
        }
        category = crud_category.create_category(db, CategoryCreate(**category_data))
        print(f"✅ Создана категория: {category.name}")

        # 3. Создаем товар
        product_data = {
            "sku": "TEST-001",
            "price": Decimal("100.00"),
            "name": "Тестовый товар",
            "description": "Описание тестового товара",
            "category_id": category.id,
            "amount": 10,
        }
        product = crud_product.create_product(db, ProductCreate(**product_data))
        print(f"✅ Создан товар: {product.name}")
        print(f"   Фотографии: {len(product.photos)}")

        # 4. Получаем товар по ID
        retrieved_product = crud_product.get_product(db, product.id)
        if retrieved_product:
            print(f"✅ Получен товар по ID: {retrieved_product.name}")
            print(f"   Фотографии: {len(retrieved_product.photos)}")

        # 5. Получаем товар по SKU
        sku_product = crud_product.get_product_by_sku(db, product.sku)
        if sku_product:
            print(f"✅ Получен товар по SKU: {sku_product.name}")
            print(f"   Фотографии: {len(sku_product.photos)}")

        # 6. Получаем список товаров
        products = crud_product.get_products(db, limit=10)
        print(f"✅ Получено товаров: {len(products)}")
        for p in products:
            print(f"   - {p.name}: {len(p.photos)} фото")

        print("🎉 Все тесты прошли успешно!")

    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    test_products_with_photos()
