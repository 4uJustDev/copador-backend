from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    sysname: str = Field(..., min_length=1, max_length=100, regex=r"^[a-z0-9-]+$")
    is_leaf: bool = False


class CategoryCreate(CategoryBase):
    parent_id: Optional[int] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    sysname: Optional[str] = Field(
        None, min_length=1, max_length=100, regex=r"^[a-z0-9-]+$"
    )
    parent_id: Optional[int] = None
    is_leaf: Optional[bool] = None


class CategoryOut(CategoryBase):
    id: int
    parent_id: Optional[int] = None
    children: List["CategoryOut"] = []

    class Config:
        from_attributes = True


# Для рекурсивной схемы
CategoryOut.model_rebuild()
