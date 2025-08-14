from uuid import UUID

from demo_api.dto import (
    CreateRoleRequest,
    Role,
    UserDetailed,
)
from demo_api.storage.protocol import RolesRepository


class RolesUseCases:
    def __init__(self, roles_repo: RolesRepository):
        self.roles_repo: RolesRepository = roles_repo

    async def list_roles(self) -> list[Role]:
        """
        Lists all roles in system.

        :return: List of roles objects.
        """
        return await self.roles_repo.list_roles()

    async def create_role(self, requested_by: UserDetailed, role: CreateRoleRequest) -> Role:
        """
        Creates a new role for user.

        :param requested_by: User who requests creation of a role.
        :param role: Information about the role.
        :return: Role information.
        :raise PermissionError: If user doesn't have permission to edit roles.
        """
        if not requested_by.user_permissions.edit_roles:
            raise PermissionError(f"User {requested_by.user_id} can't edit roles")

        return await self.roles_repo.create_role(role)

    async def update_role(self, requested_by: UserDetailed, updated_role: Role) -> Role:
        """
        Updates an existing role with new information.

        :param requested_by: User who requests update of a role.
        :param updated_role: Data with roles new information.
        :return: New role information.
        :raise NotFoundError: Role was not found in database.
        :raise PermissionError: If user doesn't have permission to edit roles.
        """
        if not requested_by.user_permissions.edit_roles:
            raise PermissionError(f"User {requested_by.user_id} can't edit roles")

        return await self.roles_repo.update_role(updated_role)

    async def delete_role(self, requested_by: UserDetailed, role_id: int) -> bool:
        """
        Removes a role from database.

        :param requested_by: User who requests deletion of a role.
        :param role_id: What role to delete by its ID.
        :return: Has role been deleted.
        :raise NotFoundError: If role has not been found.
        :raise PermissionError: If user doesn't have permission to edit roles.
        """
        if not requested_by.user_permissions.edit_roles:
            raise PermissionError(f"User {requested_by.user_id} can't edit roles")

        return await self.roles_repo.delete_role(role_id)

    async def assign_role_to_user(self, requested_by: UserDetailed, user_id: UUID, role_id: int) -> bool:
        """
        Assigns a role to a user.

        :param requested_by: User who requests assignment of a role.
        :param user_id: User identifier.
        :param role_id: ID of a role to assign to user.
        :return: Flag signifying role has been assigned to a user.
        :raise IntegrityError: If user already has the same role,
        or if user or role are is not in database.
        :raise PermissionError: If user doesn't have permission to edit roles,
        or tries to updates himself.
        """
        if not requested_by.user_permissions.edit_roles:
            raise PermissionError(f"User {requested_by.user_id} can't edit roles")

        if requested_by.user_id == role_id:
            raise PermissionError("User can't update their own roles")

        return await self.roles_repo.assign_role_to_user(user_id, role_id)

    async def remove_role_from_user(self, requested_by: UserDetailed, user_id: UUID, role_id: int) -> bool:
        """
        Removes assigned role from user.

        :param requested_by: User who requests removal of a role.
        :param user_id: User identifier.
        :param role_id: Role to remove from user.
        :return: Has role been removed.
        :raise PermissionError: If user doesn't have permission to edit roles,
        or tries to updates himself.
        """
        if not requested_by.user_permissions.edit_roles:
            raise PermissionError(f"User {requested_by.user_id} can't edit roles")

        if requested_by.user_id == role_id:
            raise PermissionError("User can't update their own roles")

        return await self.roles_repo.remove_role_from_user(user_id, role_id)
