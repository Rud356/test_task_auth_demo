from demo_api.dto import CreateRoleRequest, Resource, ResourceDetails, ResourcePermissionsUpdate, Role
from .fixtures import *


async def test_creating_resource(
    resources_repo: ResourceRepositorySQLA,
    new_registered_user: User
):
    data: Resource = await resources_repo.create_resource(
        author=new_registered_user,
        content="Hello world"
    )

    assert data.content == "Hello world"
    assert data.author_id == new_registered_user.user_id


async def test_listing_all_resources(
    resources_repo: ResourceRepositorySQLA,
    new_registered_user: User
):
    data: Resource = await resources_repo.create_resource(
        author=new_registered_user,
        content="Hello world"
    )

    assert len(await resources_repo.list_resources()) >= 1


async def test_listing_author_owned_resources(
    resources_repo: ResourceRepositorySQLA,
    new_registered_user: User
):
    resources: list[Resource] = []
    for i in range(99):
        data: Resource = await resources_repo.create_resource(
            author=new_registered_user,
            content=f"{str(i)}"
        )
        resources.append(data)

    owned_resources: list[ResourceDetails] = await resources_repo.list_available_resources(
        new_registered_user.user_id
    )

    assert all(
        (resource.author_id == new_registered_user.user_id for resource in owned_resources)
    )
    assert all(
        (
            int(resource.content) in range(100)
            for resource in owned_resources
        )
    )
    assert len(owned_resources) == 99


async def test_assigning_role_permission_to_a_resource(
    user_repo: UsersRepositorySQLA,
    roles_repo: RolesRepositorySQLA,
    resources_repo: ResourceRepositorySQLA,
    hashing_settings: HashingSettings,
    new_registered_user: User
):
    demo_user: User = await register_user(
        user_repo,
        generate_credentials(),
        hashing_settings
    )

    data: Resource = await resources_repo.create_resource(
        author=new_registered_user,
        content="Hello world"
    )

    assert data.content == "Hello world"
    assert data.author_id == new_registered_user.user_id

    assert len(
        await resources_repo.list_available_resources(
            user_id=demo_user.user_id
        )
    ) == 0
    assert len(
        await resources_repo.list_available_resources(
            user_id=new_registered_user.user_id
        )
    ) == 1

    new_role: Role = await roles_repo.create_role(
        CreateRoleRequest(role_name=f"demo_role {secrets.token_urlsafe(4)}")
    )
    await roles_repo.assign_role_to_user(demo_user.user_id, new_role.role_id)
    assert (await user_repo.get_user(demo_user.user_id)).roles == [new_role]

    assert await resources_repo.set_roles_permissions_on_resource(
        data.resource_id,
        ResourcePermissionsUpdate(
            role_id=new_role.role_id,
            can_view_resource=True,
            can_edit_resource=False
        )
    )

    available_resources: list[ResourceDetails] = await resources_repo.list_available_resources(
        user_id=demo_user.user_id
    )
    assert len(available_resources) == 1
    assert available_resources[0].resource_id == data.resource_id

    assert await resources_repo.set_roles_permissions_on_resource(
        data.resource_id,
        ResourcePermissionsUpdate(
            role_id=new_role.role_id,
            can_view_resource=True,
            can_edit_resource=True
        )
    )

    available_resources = await resources_repo.list_available_resources(
        user_id=demo_user.user_id
    )
    assert len(available_resources) == 1
    assert available_resources[0].resource_id == data.resource_id

    assert await resources_repo.set_roles_permissions_on_resource(
        data.resource_id,
        ResourcePermissionsUpdate(
            role_id=new_role.role_id,
            can_view_resource=False,
            can_edit_resource=True
        )
    )

    available_resources = await resources_repo.list_available_resources(
        user_id=demo_user.user_id
    )
    assert len(available_resources) == 1
    assert available_resources[0].resource_id == data.resource_id

    assert await resources_repo.set_roles_permissions_on_resource(
        data.resource_id,
        ResourcePermissionsUpdate(
            role_id=new_role.role_id,
            can_view_resource=False,
            can_edit_resource=False
        )
    )

    available_resources = await resources_repo.list_available_resources(
        user_id=demo_user.user_id
    )
    assert len(available_resources) == 0
