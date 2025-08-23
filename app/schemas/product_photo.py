from pydantic import BaseModel, Field
from typing import Optional


class ProductPhotoBase(BaseModel):
    filename: str = Field(..., min_length=1)
    filepath: str = Field(..., min_length=1)
    thumbpath: str = Field(..., min_length=1)
    is_main: bool = False
    sort_order: int = Field(default=0, ge=0)


class ProductPhotoCreate(ProductPhotoBase):
    product_id: int


class ProductPhotoUpdate(BaseModel):
    filename: Optional[str] = Field(None, min_length=1)
    filepath: Optional[str] = Field(None, min_length=1)
    thumbpath: Optional[str] = Field(None, min_length=1)
    is_main: Optional[bool] = None
    sort_order: Optional[int] = Field(None, ge=0)


class ProductPhotoOut(ProductPhotoBase):
    id: int
    product_id: int

    class Config:
        from_attributes = True
