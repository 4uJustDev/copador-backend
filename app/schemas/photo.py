from pydantic import BaseModel, ConfigDict
from typing import Optional


class PhotoOut(BaseModel):
    id: int
    filename: str
    filepath: str
    thumbpath: str

    model_config = ConfigDict(from_attributes=True)
