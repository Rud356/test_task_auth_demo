
from pydantic import BaseModel, Field


class PasswordUpdate(BaseModel):
    password_updated_value: str = Field(
        min_length=8, max_length=64
    )
