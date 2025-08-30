"""
Сервис для обработки расширенной информации о товарах
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.product import Product


class ProductExtensionService:
    """Сервис для добавления расширенной информации к товарам"""

    @staticmethod
    def get_extended_info(
        product: Product, category_sysname: str
    ) -> Optional[Dict[str, Any]]:
        """Получить расширенную информацию для товара в зависимости от типа"""

        if category_sysname == "carpet":
            return ProductExtensionService._get_carpet_info(product)
        else:
            return None

    @staticmethod
    def _get_carpet_info(product: Product) -> Optional[Dict[str, Any]]:
        """Получить информацию о ковре"""
        if hasattr(product, "carpet") and product.carpet:
            return {
                "width": product.carpet.width,
                "length": product.carpet.length,
                "material": product.carpet.material,
                "origin": product.carpet.origin,
                "age": product.carpet.age,
            }
        return None
