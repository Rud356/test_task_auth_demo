from demo_api.dto import CreateRoleRequest, Role, UserDetailed
from .fixtures import *


async def test_creating_and_fetching_role(roles_repo: RolesRepositorySQLA):
    new_role: Role = await roles_repo.create_role(
        CreateRoleRequest(role_name=f"Test role {secrets.token_urlsafe(6)}")
    )
    assert new_role in await roles_repo.list_roles()


async def test_deleting_role(roles_repo: RolesRepositorySQLA):
    last_role: Role | None = None
    for _ in range(10):
        last_role = await roles_repo.create_role(
            CreateRoleRequest(role_name=f"Test role {secrets.token_urlsafe(6)}")
        )

    await roles_repo.delete_role(last_role.role_id)

    assert last_role is not None
    assert last_role not in await roles_repo.list_roles()


async def test_updating_role(roles_repo: RolesRepositorySQLA):
    new_role: Role = await roles_repo.create_role(
        CreateRoleRequest(role_name=f"Test role {secrets.token_urlsafe(6)}")
    )
    updated_role: Role = await roles_repo.update_role(
        Role(
            role_id=new_role.role_id,
            role_name=f"Test update {new_role.role_name}"
        )
    )
    roles_list: list[Role] = await roles_repo.list_roles()

    assert new_role != updated_role
    assert new_role not in roles_list
    assert updated_role in roles_list
    assert updated_role.role_name.startswith("Test update")


async def test_creating_and_assigning_role(
    user_repo: UsersRepositorySQLA,
    roles_repo: RolesRepositorySQLA,
    new_registered_user: User
):
    new_role: Role = await roles_repo.create_role(
        CreateRoleRequest(role_name=f"Test role {secrets.token_urlsafe(6)}")
    )
    assert new_role in await roles_repo.list_roles()
    await roles_repo.assign_role_to_user(new_registered_user.user_id, new_role.role_id)

    updated_user_details: UserDetailed = await user_repo.get_user(new_registered_user.user_id)

    assert new_role in updated_user_details.roles


async def test_assigning_and_removing_role_from_user(
    user_repo: UsersRepositorySQLA,
    roles_repo: RolesRepositorySQLA,
    new_registered_user: User
):
    last_role: Role | None = None
    for _ in range(10):
        last_role = await roles_repo.create_role(
            CreateRoleRequest(role_name=f"Test role {secrets.token_urlsafe(6)}")
        )
        await roles_repo.assign_role_to_user(new_registered_user.user_id, last_role.role_id)

    assert last_role in await roles_repo.list_roles()
    updated_user_details: UserDetailed = await user_repo.get_user(new_registered_user.user_id)

    assert last_role in updated_user_details.roles
    assert len(updated_user_details.roles) == 10

    await roles_repo.remove_role_from_user(new_registered_user.user_id, last_role.role_id)
    updated_user_details = await user_repo.get_user(new_registered_user.user_id)
    assert last_role in await roles_repo.list_roles()
    assert last_role not in updated_user_details.roles
    assert len(updated_user_details.roles) == 9
