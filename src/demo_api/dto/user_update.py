from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class UserUpdate(BaseModel):
    """
    Represents user update details request information.
    """
    user_id: UUID
    email: Optional[EmailStr]
    name: Optional[str] = Field(
        min_length=1, max_length=255, description="Users name"
    )
    surname: Optional[str] = Field(
        min_length=1, max_length=255, description="Users surname"
    )
    third_name: Optional[str] = Field(
        min_length=1, max_length=255, description="Users third name"
    )
