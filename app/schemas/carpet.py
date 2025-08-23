from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class CarpetBase(BaseModel):
    width: Optional[Decimal] = Field(None, ge=0)
    length: Optional[Decimal] = Field(None, ge=0)
    material: Optional[str] = Field(None, max_length=100)
    origin: Optional[str] = Field(None, max_length=100)
    age: Optional[str] = Field(None, max_length=100)
    condition: Optional[str] = Field(None, max_length=100)


class CarpetCreate(CarpetBase):
    product_id: int


class CarpetUpdate(BaseModel):
    width: Optional[Decimal] = Field(None, ge=0)
    length: Optional[Decimal] = Field(None, ge=0)
    material: Optional[str] = Field(None, max_length=100)
    origin: Optional[str] = Field(None, max_length=100)
    age: Optional[str] = Field(None, max_length=100)
    condition: Optional[str] = Field(None, max_length=100)


class CarpetOut(CarpetBase):
    id: int
    product_id: int

    class Config:
        from_attributes = True


class CarpetWithProduct(CarpetOut):
    product: "ProductOut"

    class Config:
        from_attributes = True


# Для рекурсивной схемы
from .product import ProductOut

CarpetWithProduct.model_rebuild()
