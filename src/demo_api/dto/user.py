from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    """
    Represents user information.
    """
    user_id: UUID
    name: str = Field(
        min_length=1, max_length=255, description="Users name"
    )
    surname: str = Field(
        min_length=1, max_length=255, description="Users surname"
    )
    third_name: Optional[str] = Field(
        min_length=1, max_length=255, description="Users third name"
    )
    is_active: bool
