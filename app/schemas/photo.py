from pydantic import BaseModel
from typing import Optional


class PhotoOut(BaseModel):
    id: int
    filename: str
    filepath: str
    thumbpath: str

    class Config:
        from_attributes = True
