from pydantic import BaseModel, Field, field_validator
from pydantic import ConfigDict
from typing import Optional, List
from datetime import datetime
import re


class ProductTypeBase(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=100, description="Название типа товара"
    )
    sysname: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9-]+$",
        description="Системное имя (только латинские буквы, цифры и дефисы)",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Название типа товара не может быть пустым")
        return v.strip()

    @field_validator("sysname")
    @classmethod
    def validate_sysname(cls, v):
        if not v.strip():
            raise ValueError("Системное имя не может быть пустым")
        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError(
                "Системное имя может содержать только латинские буквы в нижнем регистре, цифры и дефисы"
            )
        return v.lower().strip()


class ProductTypeCreate(ProductTypeBase):
    pass


class ProductTypeUpdate(BaseModel):
    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Название типа товара"
    )
    sysname: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9-]+$",
        description="Системное имя (только латинские буквы, цифры и дефисы)",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Название типа товара не может быть пустым")
        return v.strip() if v else v

    @field_validator("sysname")
    @classmethod
    def validate_sysname(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("Системное имя не может быть пустым")
            if not re.match(r"^[a-z0-9-]+$", v):
                raise ValueError(
                    "Системное имя может содержать только латинские буквы в нижнем регистре, цифры и дефисы"
                )
            return v.lower().strip()
        return v


class ProductTypeOut(ProductTypeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
