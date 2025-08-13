import secrets
from uuid import UUID

import pytest

from demo_api.dto import SessionData, User, UserAuthentication, UserDetailed, UserPermissions
from demo_api.dto.user_registration import UserRegistration
from demo_api.dto.user_update import UserUpdate
from demo_api.storage.exceptions import NotFoundError
from demo_api.storage.sqla_implementation.users_usecase_sqla import UsersRepositorySQLA
from .fixtures import *

@pytest.fixture()
def user_usecase(transaction: TransactionSQLA) -> UsersRepositorySQLA:
    return UsersRepositorySQLA(transaction)


@pytest.fixture()
def user_credentials() -> UserRegistration:
    return UserRegistration(
        email=f"demo_email{secrets.token_urlsafe(16)}@example.com",
        name=f"test_{secrets.token_urlsafe(5)}",
        surname=f"test1_{secrets.token_urlsafe(5)}",
        third_name=f"test2_{secrets.token_urlsafe(5)}",
        password=f"DemoPass12{secrets.token_urlsafe(5)}"
    )


async def test_user_registration(
    user_usecase: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    resulting_user: User = await user_usecase.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )
    assert resulting_user.user_id and resulting_user.is_active


async def test_user_authentication(
    user_usecase: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    resulting_user: User = await user_usecase.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )

    authenticated_user: SessionData = await user_usecase.login(
        UserAuthentication(
            email=user_credentials.email,
            password=user_credentials.password
        ),
        hashing_settings
    )

    assert resulting_user.user_id == authenticated_user.user_id


async def test_user_authentication_for_missing_user(
    user_usecase: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    with pytest.raises(NotFoundError):
        await user_usecase.login(
            UserAuthentication(
                email=user_credentials.email,
                password=user_credentials.password
            ),
            hashing_settings
        )


async def test_user_authentication_with_invalid_password(
    user_usecase: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    await user_usecase.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )

    with pytest.raises(ValueError):
        await user_usecase.login(
            UserAuthentication(
                email=user_credentials.email,
                password=user_credentials.password + "12345678"
            ),
            hashing_settings
        )


async def test_user_session_auth(
    user_usecase: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    await user_usecase.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )

    authenticated_user: SessionData = await user_usecase.login(
        UserAuthentication(
            email=user_credentials.email,
            password=user_credentials.password
        ),
        hashing_settings
    )

    user_from_session: UserDetailed = await user_usecase.get_user_by_session(
        authenticated_user.session_id
    )

    assert authenticated_user.user_id == user_from_session.user_id


async def test_user_session_auth_via_not_existing_session(
    user_usecase: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    await user_usecase.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )

    authenticated_user: SessionData = await user_usecase.login(
        UserAuthentication(
            email=user_credentials.email,
            password=user_credentials.password
        ),
        hashing_settings
    )

    with pytest.raises(NotFoundError):
        await user_usecase.get_user_by_session(
            authenticated_user.session_id + "12345678"
        )


async def test_fetching_user_details(
    user_usecase: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    registered_user: User = await user_usecase.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )

    fetched_user: UserDetailed = await user_usecase.get_user(
        registered_user.user_id
    )

    assert fetched_user.user_id == registered_user.user_id
    assert fetched_user.name == registered_user.name


async def test_user_session_termination(
    user_usecase: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    await user_usecase.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )

    authenticated_user: SessionData = await user_usecase.login(
        UserAuthentication(
            email=user_credentials.email,
            password=user_credentials.password
        ),
        hashing_settings
    )

    user_from_session: UserDetailed = await user_usecase.get_user_by_session(
        authenticated_user.session_id
    )

    assert authenticated_user.user_id == user_from_session.user_id

    assert await user_usecase.terminate_session(
        authenticated_user
    )

    with pytest.raises(NotFoundError):
        await user_usecase.get_user_by_session(
            authenticated_user.session_id
        )


async def test_user_terminating_all_sessions(
    user_usecase: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    user: User = await user_usecase.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )

    sessions: list[SessionData] = []
    for _ in range(5):
        authenticated_user: SessionData = await user_usecase.login(
            UserAuthentication(
                email=user_credentials.email,
                password=user_credentials.password
            ),
            hashing_settings
        )
        sessions.append(authenticated_user)

        assert (await user_usecase.get_user_by_session(
            authenticated_user.session_id
        )).user_id == user.user_id

    assert await user_usecase.terminate_all_sessions(
        user.user_id
    )

    for user_session in sessions:
        with pytest.raises(NotFoundError):
            await user_usecase.get_user_by_session(
                user_session.session_id
            )


async def test_fetching_many_users(
    user_usecase: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    for i in range(10):
        user_credentials.email = f"{i}{user_credentials.email}"
        await user_usecase.register_user(
            user_credentials,
            UserPermissions(),
            hashing_settings
        )

    assert len(await user_usecase.list_users(limit=10)) == 10


async def test_terminating_user(
    user_usecase: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    await user_usecase.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )

    authenticated_user: SessionData = await user_usecase.login(
        UserAuthentication(
            email=user_credentials.email,
            password=user_credentials.password
        ),
        hashing_settings
    )

    user_from_session: UserDetailed = await user_usecase.get_user_by_session(
        authenticated_user.session_id
    )

    assert authenticated_user.user_id == user_from_session.user_id

    assert await user_usecase.terminate_user(authenticated_user.user_id)

    with pytest.raises(NotFoundError):
        await user_usecase.get_user_by_session(
            authenticated_user.session_id
        )

    with pytest.raises(NotFoundError):
        await user_usecase.login(
            UserAuthentication(
                email=user_credentials.email,
                password=user_credentials.password
            ),
            hashing_settings
        )

async def test_fetching_many_users_with_deactivated(
    user_usecase: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    for i in range(10):
        user_credentials.email = f"{i}{user_credentials.email}"
        await user_usecase.register_user(
            user_credentials,
            UserPermissions(),
            hashing_settings
        )

    assert len(await user_usecase.list_users(limit=10, include_deactivated=True)) == 10


async def test_user_changing_password(
    user_usecase: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    user: User = await user_usecase.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )

    sessions: list[SessionData] = []
    for _ in range(5):
        authenticated_user: SessionData = await user_usecase.login(
            UserAuthentication(
                email=user_credentials.email,
                password=user_credentials.password
            ),
            hashing_settings
        )
        sessions.append(authenticated_user)

        assert (await user_usecase.get_user_by_session(
            authenticated_user.session_id
        )).user_id == user.user_id

    assert await user_usecase.change_user_password(
        user.user_id, "TestPassword12345678", hashing_settings
    )

    for user_session in sessions:
        with pytest.raises(NotFoundError):
            await user_usecase.get_user_by_session(
                user_session.session_id
            )


async def test_updating_user_data(
    user_usecase: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    user: User = await user_usecase.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )
    update_details: UserUpdate = UserUpdate(
        user_id=user.user_id,
        email=f"example_for_testing_updates_{secrets.token_urlsafe(8)}@example.com",
        name="Hello",
        surname="World",
        third_name="Some text"
    )

    updated_details: UserDetailed = await user_usecase.update_user_details(update_details)
    assert updated_details == await user_usecase.get_user(user.user_id)
