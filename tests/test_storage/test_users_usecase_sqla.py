import secrets

import pytest

from demo_api.dto import SessionData, User, UserAuthentication, UserDetailed, UserPermissions
from demo_api.dto.user_registration import UserRegistration
from demo_api.storage.exceptions import NotFoundError
from demo_api.storage.sqla_implementation.users_usecase_sqla import UsersUsecaseSQLA
from .fixtures import *

@pytest.fixture()
def user_usecase(transaction: TransactionSQLA) -> UsersUsecaseSQLA:
    return UsersUsecaseSQLA(transaction)


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
    user_usecase: UsersUsecaseSQLA,
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
    user_usecase: UsersUsecaseSQLA,
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
    user_usecase: UsersUsecaseSQLA,
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
    user_usecase: UsersUsecaseSQLA,
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
    user_usecase: UsersUsecaseSQLA,
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
    user_usecase: UsersUsecaseSQLA,
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
    user_usecase: UsersUsecaseSQLA,
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
    user_usecase: UsersUsecaseSQLA,
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
