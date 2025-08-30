from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
import re


class ProductBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=50, description="SKU товара")
    price: Decimal = Field(
        ..., ge=0, description="Цена товара (не может быть отрицательной)"
    )
    name: str = Field(..., min_length=1, max_length=200, description="Название товара")
    description: Optional[str] = Field(None, description="Описание товара")
    category_id: Optional[int] = Field(None, description="ID категории")
    amount: int = Field(
        default=0,
        ge=0,
        description="Количество на складе (не может быть отрицательным)",
    )

    @field_validator("sku")
    @classmethod
    def validate_sku(cls, v):
        if not v.strip():
            raise ValueError("SKU не может быть пустым")
        if not re.match(r"^[A-Za-z0-9\-_]+$", v):
            raise ValueError(
                "SKU может содержать только буквы, цифры, дефисы и подчеркивания"
            )
        return v.strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Название товара не может быть пустым")
        return v.strip()

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        if v < 0:
            raise ValueError("Цена товара не может быть отрицательной")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError("Количество товара не может быть отрицательным")
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: Optional[str] = Field(
        None, min_length=1, max_length=50, description="SKU товара"
    )
    price: Optional[Decimal] = Field(
        None, ge=0, description="Цена товара (не может быть отрицательной)"
    )
    name: Optional[str] = Field(
        None, min_length=1, max_length=200, description="Название товара"
    )
    description: Optional[str] = Field(None, description="Описание товара")
    category_id: Optional[int] = Field(None, description="ID категории")
    amount: Optional[int] = Field(
        None, ge=0, description="Количество на складе (не может быть отрицательным)"
    )

    @field_validator("sku")
    @classmethod
    def validate_sku(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("SKU не может быть пустым")
            if not re.match(r"^[A-Za-z0-9\-_]+$", v):
                raise ValueError(
                    "SKU может содержать только буквы, цифры, дефисы и подчеркивания"
                )
            return v.strip()
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Название товара не может быть пустым")
        return v.strip() if v else v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError("Цена товара не может быть отрицательной")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v is not None and v < 0:
            raise ValueError("Количество товара не может быть отрицательным")
        return v


from app.schemas.product_photo import ProductPhotoOut


class ProductOut(ProductBase):
    id: int
    category_name: Optional[str] = None
    category_product_type_sysname: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]
    photos: List[ProductPhotoOut] = []

    model_config = ConfigDict(from_attributes=True)


class ProductWithExtendedInfo(ProductOut):
    """Универсальная схема для товаров с дополнительной информацией"""

    extended_info: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)
