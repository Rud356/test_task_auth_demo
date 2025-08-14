from demo_api.dto import (
    Resource,
    ResourceDetails,
    ResourcePermissionsDetails,
    ResourcePermissionsUpdate,
    Role,
    User,
    UserDetailed,
)
from demo_api.storage.protocol import ResourceRepository
from tests.test_storage.fixtures import user_repo


class ResourceUseCases:
    def __init__(self, resource_repo: ResourceRepository):
        self.resource_repo: ResourceRepository = resource_repo

    async def create_resource(self, author: User, content: str) -> Resource:
        """
        Creates new resource.

        :param author: User who creates a resource.
        :param content: Content of resource.
        :return: Newly created resource information.
        :raises DataIntegrityError: If reference to user is invalid.
        """
        return await self.resource_repo.create_resource(author, content)

    async def list_all_resources(
        self,
        requested_by: UserDetailed,
        limit: int = 100,
        offset: int = 0
    ) -> list[ResourceDetails]:
        """
        Lists resources.

        :param requested_by: User who requests all resources view.
        :param limit: Limits how many records to fetch.
        :param offset: How many records to skip.
        :return: List of resources with permissions details.
        :raise PermissionError: If user can't view all resources.
        """
        if not requested_by.user_permissions.view_all_resources:
            raise PermissionError("User can't view all resources")

        return await self.resource_repo.list_resources(limit, offset)

    async def list_available_resources(
        self,
        requested_by: UserDetailed,
        limit: int = 100,
        offset: int = 0
    ) -> list[ResourceDetails]:
        """
        Lists resources.

        :param requested_by: User who requests resources view.
        :param limit: Limits how many records to fetch.
        :param offset: How many records to skip.
        :return: List of resources with permissions details.
        :raise PermissionError: If user can't view all resources.
        """
        return await self.resource_repo.list_available_resources(
            requested_by.user_id, limit, offset
        )

    async def edit_resource(self, requested_by: UserDetailed, resource_id: int, content: str) -> Resource:
        """
        Changes resource content.

        :param requested_by: User who requests editing of a resource.
        :param resource_id: ID of a resource to edit.
        :param content: New content of resource.
        :return: Updated resource information.
        :raise NotFoundError: If resource is not in database.
        :raise PermissionError: If user can't edit this resource.
        """
        resource: ResourceDetails = await self.resource_repo.get_resource_by_id(resource_id)
        can_user_edit_resource: bool = self._check_resource_permissions_for_editing(
            resource, requested_by
        )

        if can_user_edit_resource:
            return await self.resource_repo.edit_resource(resource_id, content)

        raise PermissionError("User does not have access to editing this resource")

    async def get_resource_by_id(self, requested_by: UserDetailed, resource_id: int) -> ResourceDetails:
        """
        Fetches resource by ID.

        :param requested_by: User who requests a resource.
        :param resource_id: ID of resource to fetch.
        :return: Resource information.
        :raise NotFoundError: If resource is not in database.
        :raise PermissionError: If user can't view this resource.
        """
        resource: ResourceDetails = await self.resource_repo.get_resource_by_id(resource_id)
        can_user_view_resource: bool = self._check_resource_permissions_for_viewing(
            resource, requested_by
        )

        if can_user_view_resource:
            return await self.resource_repo.get_resource_by_id(resource_id)

        raise PermissionError("User does not have access to editing this resource")

    async def set_roles_permissions_on_resource(
        self, requested_by: UserDetailed, resource_id: int, resource_permissions: ResourcePermissionsUpdate
    ) -> bool:
        """
        Changes permissions to a resource.

        :param requested_by: User who requests editing of a resource.
        :param resource_id: ID of a resource.
        :param resource_permissions: New permissions for a role to resource.
        :return: Has permissions been set.
        :raise PermissionError: If user can't edit this resource because of lacking permissions or
        not being an author of the resource.
        """
        resource: ResourceDetails = await self.resource_repo.get_resource_by_id(resource_id)
        if (
            resource.author_id != requested_by.user_id or
            not requested_by.user_permissions.administrate_resources
        ):
            raise PermissionError("User can not edit resource access")

        return await self.resource_repo.set_roles_permissions_on_resource(resource_id, resource_permissions)

    @staticmethod
    def _check_resource_permissions_for_editing(resource: ResourceDetails, user: UserDetailed) -> bool:
        if user.user_permissions.administrate_resources:
            return True

        can_edit_via_role: bool = False
        resource: ResourceDetails = resource
        resource_roles: dict[int, ResourcePermissionsDetails] = {
            role_permissions.role_id: role_permissions
            for role_permissions in resource.roles_permissions
        }

        for role in user.roles:
            found_role = resource_roles.get(role.role_id)
            if found_role is not None and found_role.can_edit_resource:
                can_edit_via_role = True
                break

        return can_edit_via_role

    @staticmethod
    def _check_resource_permissions_for_viewing(resource: ResourceDetails, user: UserDetailed) -> bool:
        if user.user_permissions.administrate_resources:
            return True

        can_view_via_role: bool = False
        resource: ResourceDetails = resource
        resource_roles: dict[int, ResourcePermissionsDetails] = {
            role_permissions.role_id: role_permissions
            for role_permissions in resource.roles_permissions
        }

        for role in user.roles:
            found_role = resource_roles.get(role.role_id)
            if found_role is not None and found_role.can_edit_resource:
                can_view_via_role = True
                break

        return can_view_via_role
