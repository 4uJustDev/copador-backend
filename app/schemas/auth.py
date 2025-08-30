from pydantic import BaseModel, Field, ConfigDict, field_validator
import re
from typing import List, Optional
from app.schemas.role import RoleOut


class RegisterRequest(BaseModel):
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=6)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if not v:
            raise ValueError("Email cannot be empty")
        # Простая валидация email
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v.lower()


class LoginRequest(BaseModel):
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=6)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if not v:
            raise ValueError("Email cannot be empty")
        # Простая валидация email
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v.lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfileResponse(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    birth_date: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    email: str
    roles: List[RoleOut]
    profile: Optional[UserProfileResponse] = None
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)
