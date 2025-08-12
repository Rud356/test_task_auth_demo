from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SessionData(BaseModel):
    """
    Represents user session data.
    """
    user_id: UUID
    created_at: datetime
    session_id: str
    is_alive: bool
