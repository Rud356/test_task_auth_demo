from .resource import Resource
from .resource_permissions_details import ResourcePermissionsDetails


class ResourceDetails(Resource):
    roles_permissions: list[ResourcePermissionsDetails]
