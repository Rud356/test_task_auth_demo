from uuid import UUID

from pydantic import BaseModel


class UserChangedPassword(BaseModel):
    user_id: UUID
    changed_password: bool
