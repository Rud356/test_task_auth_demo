from abc import abstractmethod
from typing import Protocol, runtime_checkable
from uuid import UUID

from demo_api.dto import CreateRoleRequest
from demo_api.dto import Role


@runtime_checkable
class RolesRepository(Protocol):
    @abstractmethod
    async def list_roles(self) -> list[Role]:
        """
        Lists all roles in system.

        :return: List of roles objects.
        """

    @abstractmethod
    async def create_role(self, role: CreateRoleRequest) -> Role:
        """
        Creates a new role for user.

        :param role: Information about the role.
        :return: Role information.
        """

    @abstractmethod
    async def update_role(self, updated_role: Role) -> Role:
        """
        Updates an existing role with new information.

        :param updated_role: Data with roles new information.
        :return: New role information.
        :raise NotFoundError: Role was not found in database.
        """

    @abstractmethod
    async def delete_role(self, role_id: int) -> bool:
        """
        Removes a role from database.

        :param role_id: What role to delete by its ID.
        :return: Has role been deleted.
        :raise NotFoundError: If role has not been found.
        """

    @abstractmethod
    async def assign_role_to_user(self, user_id: UUID, role_id: int) -> bool:
        """
        Assigns a role to a user.

        :param user_id: User identifier.
        :param role_id: ID of a role to assign to user.
        :return: Flag signifying role has been assigned to a user.
        """

    @abstractmethod
    async def remove_role_from_user(self, user_id: UUID, role_id: int) -> bool:
        """
        Removes assigned role from user.

        :param user_id: User identifier.
        :param role_id: Role to remove from user.
        :return: Has role been removed.
        """
