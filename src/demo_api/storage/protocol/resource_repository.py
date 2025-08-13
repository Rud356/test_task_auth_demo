from abc import abstractmethod
from typing import Protocol, runtime_checkable
from uuid import UUID

from demo_api.dto import Resource, ResourceDetails, ResourcePermissionsUpdate, User


@runtime_checkable
class ResourceRepository(Protocol):
    @abstractmethod
    async def create_resource(self, author: User, content: str) -> Resource:
        """
        Creates new resource.

        :param author: User who creates a resource.
        :param content: Content of resource.
        :return: Newly created resource information.
        """

    @abstractmethod
    async def edit_resource(self, content: str) -> Resource:
        """
        Changes resource content.

        :param content: New content of resource.
        :return: Updated resource information.
        """

    @abstractmethod
    async def list_resources(self, limit: int = 100, offset: int = 0) -> list[ResourceDetails]:
        """
        Lists resources.

        :param limit: Limits how many records to fetch.
        :param offset: How many records to skip.
        :return: List of resources with permissions details.
        """

    @abstractmethod
    async def list_available_resources(
        self, user_id: UUID, limit: int = 100, offset: int = 0
    ) -> list[ResourceDetails]:
        """
        Fetches only available resources for specified user.

        :param user_id: Users identifier.
        :param limit: How many records to fetch.
        :param offset: How many records to skip.
        :return: List of resources with details about permissions.
        """

    @abstractmethod
    async def set_roles_permissions_on_resource(
        self, resource_id: int, resource_permissions: ResourcePermissionsUpdate
    ) -> bool:
        """
        Changes permissions to a resource.

        :param resource_id: ID of a resource.
        :param resource_permissions: New permissions for a role to resource.
        :return: Has permissions been set.
        """
