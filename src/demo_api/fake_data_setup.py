import asyncio

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from demo_api.dto import CreateRoleRequest, HashingSettings, Resource, ResourcePermissionsUpdate, User, UserPermissions
from demo_api.dto.user_registration import UserRegistration
from demo_api.storage.protocol import ResourceRepository, RolesRepository, UsersRepository
from demo_api.storage.sqla_implementation.resource_repository_sqla import ResourceRepositorySQLA
from demo_api.storage.sqla_implementation.roles_repository_sqla import RolesRepositorySQLA
from demo_api.storage.sqla_implementation.transaction import TransactionSQLA
from demo_api.storage.sqla_implementation.users_repository_sqla import UsersRepositorySQLA
from demo_api.utils.config_schema import AppConfig


async def _setup_data(
    config: AppConfig
) -> None:
    engine: AsyncEngine = create_async_engine(
        config.db_settings.connection_string,
        echo=False
    )
    session_maker: async_sessionmaker[
        AsyncSession
    ] = async_sessionmaker(
        engine,
        expire_on_commit=False
    )
    transaction: TransactionSQLA = TransactionSQLA(session_maker)
    users_repo: UsersRepository = UsersRepositorySQLA(transaction)
    roles_repo: RolesRepository = RolesRepositorySQLA(transaction)
    resources_repo: ResourceRepository = ResourceRepositorySQLA(transaction)

    # Register superuser
    superuser: User = await users_repo.register_user(
        UserRegistration(
            email="demo_superuser@example.com",
            name="Test",
            surname="Superuser",
            third_name=None,
            password="demoPASS1234"
        ),
        UserPermissions(
            edit_roles=True,
            view_all_resources=True,
            administrate_users=True,
            administrate_resources=True
        ),
        HashingSettings(
            hash_algorithm=config.security.password_hash_algorithm,
            iterations_count=config.security.password_hash_iterations
        )
    )
    role_1 = await roles_repo.create_role(CreateRoleRequest(role_name="Demo role 1"))
    role_2 = await roles_repo.create_role(CreateRoleRequest(role_name="Demo role 2"))

    await roles_repo.assign_role_to_user(superuser.user_id, role_1.role_id)

    # Register user with role 1
    roles_user: User = await users_repo.register_user(
        UserRegistration(
            email="demo_roles_1@example.com",
            name="Test",
            surname="Role 1 user",
            third_name=None,
            password="demoPASS1234"
        ),
        UserPermissions(
            edit_roles=True,
            view_all_resources=True,
            administrate_users=True,
            administrate_resources=True
        ),
        HashingSettings(
            hash_algorithm=config.security.password_hash_algorithm,
            iterations_count=config.security.password_hash_iterations
        )
    )
    await roles_repo.assign_role_to_user(roles_user.user_id, role_1.role_id)

    # Register user with role 2
    user_with_role2: User = await users_repo.register_user(
        UserRegistration(
            email="demo_role2@example.com",
            name="Test",
            surname="Role 2 user",
            third_name=None,
            password="demoPASS1234"
        ),
        UserPermissions(),
        HashingSettings(
            hash_algorithm=config.security.password_hash_algorithm,
            iterations_count=config.security.password_hash_iterations
        )
    )
    await roles_repo.assign_role_to_user(user_with_role2.user_id, role_2.role_id)

    # Register user without roles
    await users_repo.register_user(
        UserRegistration(
            email="demo_empty@example.com",
            name="Test",
            surname="Demo without permissions",
            third_name=None,
            password="demoPASS1234123"
        ),
        UserPermissions(),
        HashingSettings(
            hash_algorithm=config.security.password_hash_algorithm,
            iterations_count=config.security.password_hash_iterations
        )
    )

    # Create new resource from roles_user
    resource_1: Resource = await resources_repo.create_resource(
        roles_user, "Hello world from user!"
    )
    resource_2: Resource = await resources_repo.create_resource(
        roles_user, "Hello to users with role 2!"
    )

    await resources_repo.set_roles_permissions_on_resource(
        resource_1.resource_id,
        ResourcePermissionsUpdate(
            role_id=role_1.role_id,
            can_edit_resource=False,
            can_view_resource=True
        )
    )
    await resources_repo.set_roles_permissions_on_resource(
        resource_2.resource_id,
        ResourcePermissionsUpdate(
            role_id=role_2.role_id,
            can_edit_resource=True,
            can_view_resource=True
        )
    )


def setup_fake_data(config: AppConfig) -> None:
    asyncio.run(
        _setup_data(
            config
        )
    )
