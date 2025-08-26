from pydantic import BaseModel, Field, computed_field
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    sysname: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")


class CategoryCreate(CategoryBase):
    parent_id: Optional[int] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    sysname: Optional[str] = Field(
        None, min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$"
    )
    parent_id: Optional[int] = None


class CategoryOut(CategoryBase):
    id: int
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CategoryWithComputed(CategoryOut):
    @computed_field
    @property
    def is_leaf(self) -> bool:
        """Вычисляемое поле: является ли категория листом"""
        # Это поле будет переопределяться в CRUD операциях
        return getattr(self, "_is_leaf", False)

    @computed_field
    @property
    def children(self) -> List["CategoryWithComputed"]:
        """Вычисляемое поле: дочерние категории"""
        # Это поле будет переопределяться в CRUD операциях
        return getattr(self, "_children", [])


# Для рекурсивной схемы
CategoryWithComputed.model_rebuild()
