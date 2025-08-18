from uuid import UUID

from pydantic import BaseModel


class SessionTerminationConfirmed(BaseModel):
    user_id: UUID
    terminated: bool
