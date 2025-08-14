from typing import Sequence
from uuid import UUID

from sqlalchemy import CompoundSelect, Insert, Select, Update, and_, insert, or_, select, union_all
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.sql.selectable import ExecutableReturnsRows

from demo_api.dto import Resource, ResourceDetails, ResourcePermissionsDetails, ResourcePermissionsUpdate, User
from demo_api.storage.exceptions import DataIntegrityError, NotFoundError
from demo_api.storage.protocol import ResourceRepository
from demo_api.storage.sqla_implementation.tables import (
    AssignedRolesTable,
    ResourceTable,
    RolesPermissionsTable,
    RolesTable,
)
from demo_api.storage.sqla_implementation.transaction import TransactionSQLA


class ResourceRepositorySQLA(ResourceRepository):
    def __init__(self, transaction: TransactionSQLA):
        self.transaction: TransactionSQLA = transaction

    async def create_resource(self, author: User, content: str) -> Resource:
        async with self.transaction as tr:
            new_resource: ResourceTable = ResourceTable(
                author_id=author.user_id,
                content=content
            )
            tr.add(new_resource)

            try:
                await tr.commit()

            except IntegrityError as err:
                raise DataIntegrityError(f"User {author.user_id} likely doesn't exist") from err

        return Resource(
            resource_id=new_resource.resource_id,
            author_id=author.user_id,
            content=new_resource.content
        )

    async def edit_resource(self, resource_id: int, content: str) -> Resource:
        async with self.transaction as tr:
            try:
                resource: ResourceTable = await tr.get_one(ResourceTable, resource_id)

            except NoResultFound as err:
                raise NotFoundError(f"Resource with {resource_id} not found")

            resource.content = content
            await tr.commit()

        return Resource(
            resource_id=resource.resource_id,
            author_id=resource.author_id,
            content=str(resource.content)
        )

    async def get_resource_by_id(self, resource_id: int) -> ResourceDetails:
        async with self.transaction as tr:
            try:
                resource: ResourceTable = await tr.get_one(ResourceTable, resource_id)

            except NoResultFound as err:
                raise NotFoundError(f"Resource with {resource_id} not found")

        permissions_details: list[ResourcePermissionsDetails] = [
            ResourcePermissionsDetails(
                role_id=role_permissions.role_id,
                role_name=role_permissions.role.role_name,
                can_edit_resource=role_permissions.can_edit_resource,
                can_view_resource=role_permissions.can_view_resource
            )
            for role_permissions in resource.roles_permissions
        ]
        return ResourceDetails(
            resource_id=resource.resource_id,
            author_id=resource.author_id,
            content=resource.content,
            roles_permissions=permissions_details
        )

    async def list_resources(self, limit: int = 100, offset: int = 0) -> list[ResourceDetails]:
        query: Select[tuple[ResourceTable]] = (
            select(ResourceTable)
            .limit(limit).offset(offset)
            .order_by(ResourceTable.resource_id.desc())
        )
        resources: list[ResourceDetails] = []

        async with self.transaction as tr:
            resources_records: Sequence[ResourceTable] = (await tr.scalars(query)).all()

            for resource_record in resources_records:
                permissions_details: list[ResourcePermissionsDetails] = [
                    ResourcePermissionsDetails(
                        role_id=role_permissions.role_id,
                        role_name=role_permissions.role.role_name,
                        can_edit_resource=role_permissions.can_edit_resource,
                        can_view_resource=role_permissions.can_view_resource
                    )
                    for role_permissions in resource_record.roles_permissions
                ]
                resource: ResourceDetails = ResourceDetails(
                    resource_id=resource_record.resource_id,
                    author_id=resource_record.author_id,
                    content=resource_record.content,
                    roles_permissions=permissions_details
                )
                resources.append(resource)

        return resources

    async def list_available_resources(
        self, user_id: UUID, limit: int = 100, offset: int = 0
    ) -> list[ResourceDetails]:
        query_by_author: Select[tuple[ResourceTable]] = (
            select(ResourceTable)
            .where(ResourceTable.author_id == user_id)
        )
        query_user_specific_roles: Select[tuple[ResourceTable]] = (
            select(ResourceTable)
            .join(
                RolesPermissionsTable,
                RolesPermissionsTable.resource_id == ResourceTable.resource_id
            )
            .join(
                RolesTable,
                RolesTable.role_id == RolesPermissionsTable.role_id
            )
            .join(
                AssignedRolesTable,
                AssignedRolesTable.role_id == RolesTable.role_id
            )
            .where(
                and_(
                    AssignedRolesTable.user_id == user_id,
                    or_(
                        RolesPermissionsTable.can_edit_resource.is_(True),
                        RolesPermissionsTable.can_view_resource.is_(True)
                    )
                )
            )
        )

        query_matching: CompoundSelect[tuple[ResourceTable]] = (
            union_all(query_by_author, query_user_specific_roles)
            .order_by(ResourceTable.resource_id.desc())
            .limit(limit)
            .offset(offset)
        )
        query: ExecutableReturnsRows = (
            select(ResourceTable).from_statement(query_matching)
        )
        resources: list[ResourceDetails] = []

        async with self.transaction as tr:
            resources_records: Sequence[ResourceTable] = (await tr.scalars(query)).all()

            for resource_record in resources_records:
                permissions_details: list[ResourcePermissionsDetails] = [
                    ResourcePermissionsDetails(
                        role_id=role_permissions.role_id,
                        role_name=role_permissions.role.role_name,
                        can_edit_resource=role_permissions.can_edit_resource,
                        can_view_resource=role_permissions.can_view_resource
                    )
                    for role_permissions in resource_record.roles_permissions
                ]
                resource: ResourceDetails = ResourceDetails(
                    resource_id=resource_record.resource_id,
                    author_id=resource_record.author_id,
                    content=resource_record.content,
                    roles_permissions=permissions_details
                )
                resources.append(resource)

        return resources

    async def set_roles_permissions_on_resource(
        self,
        resource_id: int,
        resource_permissions: ResourcePermissionsUpdate
    ) -> bool:
        query_insert: Insert = insert(RolesPermissionsTable).values(
            {
                "role_id": resource_permissions.role_id,
                "resource_id": resource_id,
                "can_view_resource": resource_permissions.can_view_resource,
                "can_edit_resource": resource_permissions.can_edit_resource
            }
        )
        async with self.transaction as tr:
            try:
                await tr.execute(query_insert)
                await tr.commit()
                return True

            except IntegrityError:
                await tr.rollback()

            query_update: Update = Update(RolesPermissionsTable).values(
                {
                    "resource_id": resource_id,
                    "can_view_resource": resource_permissions.can_view_resource,
                    "can_edit_resource": resource_permissions.can_edit_resource
                }
            ).where(RolesPermissionsTable.role_id == resource_permissions.role_id)

            try:
                await tr.execute(query_update)
                await tr.commit()
                return True

            except IntegrityError:
                await tr.rollback()
                return False
