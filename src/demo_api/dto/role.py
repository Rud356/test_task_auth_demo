from pydantic import BaseModel, Field


class Role(BaseModel):
    role_id: int
    role_name: str = Field(min_length=1, max_length=64)
