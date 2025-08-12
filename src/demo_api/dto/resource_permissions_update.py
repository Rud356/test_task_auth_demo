from pydantic import BaseModel


class ResourcePermissionsUpdate(BaseModel):
    role_id: int
    can_view_resource: bool
    can_edit_resource: bool
