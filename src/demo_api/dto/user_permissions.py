from uuid import UUID

from pydantic import BaseModel, Field


class UserPermissions(BaseModel):
    """
    Represents user permissions information.
    """
    user_id: UUID
    edit_roles: bool = Field(default=False)
    view_all_resources: bool = Field(default=False)
    administrate_users: bool = Field(default=False)
    administrate_resources: bool = Field(default=False)
