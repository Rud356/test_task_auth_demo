from uuid import UUID

from pydantic import BaseModel


class UserTerminated(BaseModel):
    user_id: UUID
    is_active: bool
