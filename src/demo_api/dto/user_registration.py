from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class UserRegistration(BaseModel):
    """
    Represents user information.
    """
    user_id: UUID
    email: EmailStr
    name: str = Field(
        min_length=1, max_length=255, description="Users name"
    )
    surname: str = Field(
        min_length=1, max_length=255, description="Users surname"
    )
    third_name: Optional[str] = Field(
        min_length=1, max_length=255, description="Users third name"
    )
    password: str = Field(
        min_length=8, max_length=64,
        pattern=r"^[A-Za-z\d]{8,64}$"
    )
