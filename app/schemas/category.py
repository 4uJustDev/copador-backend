from pydantic import BaseModel, Field
from pydantic import ConfigDict  # pydantic v2
from typing import Optional, List
from datetime import datetime

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    sysname: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")

class CategoryCreate(CategoryBase):
    parent_id: Optional[int] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    sysname: Optional[str] = Field(None, min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    parent_id: Optional[int] = None

class CategoryOut(CategoryBase):
    id: int
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class CategoryWithComputed(CategoryOut):
    is_leaf: bool = False
    children: List["CategoryWithComputed"] = Field(default_factory=list)

CategoryWithComputed.model_rebuild()
