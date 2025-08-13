from typing import Sequence
from uuid import UUID

from sqlalchemy import Select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm.exc import StaleDataError

from demo_api.dto import CreateRoleRequest, Role
from demo_api.storage.exceptions import NotFoundError
from demo_api.storage.protocol import RolesRepository
from demo_api.storage.sqla_implementation.tables import AssignedRolesTable, RolesTable
from demo_api.storage.sqla_implementation.transaction import TransactionSQLA


class RolesRepositorySQLA(RolesRepository):
    def __init__(self, transaction: TransactionSQLA):
        self.transaction: TransactionSQLA = transaction

    async def list_roles(self) -> list[Role]:
        async with self.transaction as tr:
            query: Select[tuple[RolesTable, ...]] = Select(RolesTable)
            all_roles: Sequence[RolesTable] = (await tr.scalars(query)).all()

        return [
            Role(role_id=role_data.role_id, role_name=role_data.role_name)
            for role_data in all_roles
        ]

    async def create_role(self, role: CreateRoleRequest) -> Role:
        async with self.transaction as tr:
            new_role: RolesTable = RolesTable(role_name=role.role_name)
            tr.add(new_role)
            await tr.commit()

        return Role(role_id=new_role.role_id, role_name=new_role.role_name)

    async def update_role(self, updated_role: Role) -> Role:
        async with self.transaction as tr:
            try:
                current_role: RolesTable = await tr.get_one(
                    RolesTable, updated_role.role_id
                )

            except NoResultFound as err:
                raise NotFoundError("Role was not found") from err

            current_role.role_name = updated_role.role_name
            await tr.commit()

        return Role(role_id=current_role.role_id, role_name=str(current_role.role_name))

    async def delete_role(self, role_id: int) -> bool:
        async with self.transaction as tr:
            try:
                current_role: RolesTable = await tr.get_one(
                    RolesTable, role_id
                )

            except NoResultFound as err:
                raise NotFoundError("Role was not found") from err

            try:
                await tr.delete(current_role)
                await tr.commit()

            except StaleDataError:
                return False

        return True

    async def assign_role_to_user(self, user_id: UUID, role_id: int) -> bool:
        async with self.transaction as tr:
            role_assignment = AssignedRolesTable(user_id=user_id, role_id=role_id)
            tr.add(role_assignment)

            try:
                await tr.commit()

            except IntegrityError:
                return False

        return True

    async def remove_role_from_user(self, user_id: UUID, role_id: int) -> bool:
        async with self.transaction as tr:
            try:
                current_role_assignment: AssignedRolesTable = await tr.get_one(
                    AssignedRolesTable, {"user_id": user_id, "role_id": role_id}
                )

            except NoResultFound as err:
                raise NotFoundError("Role was not found") from err

            await tr.delete(current_role_assignment)

            try:
                await tr.commit()

            except (IntegrityError, StaleDataError):
                return False

        return True
