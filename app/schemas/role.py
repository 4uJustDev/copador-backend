from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)


class RoleOut(RoleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
