from .resource_permissions_update import ResourcePermissionsUpdate


class ResourcePermissionsDetails(ResourcePermissionsUpdate):
    role_id: int
    role_name: str
