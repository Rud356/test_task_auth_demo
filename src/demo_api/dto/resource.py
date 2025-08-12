from uuid import UUID

from pydantic import BaseModel, Field


class Resource(BaseModel):
    """
    Represents resource information.
    """
    resource_id: int
    author_id: UUID
    content: str = Field(min_length=1, max_length=2048)
