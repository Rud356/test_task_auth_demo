from pydantic import BaseModel

from demo_api.dto import ResourcePermissionsUpdate


class ResourcePermissionsModified(BaseModel):
    resource_id: int
    new_permissions: ResourcePermissionsUpdate
