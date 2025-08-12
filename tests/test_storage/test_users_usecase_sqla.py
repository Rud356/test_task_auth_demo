import secrets

from sqlalchemy import select

from demo_api.dto import SessionData, User, UserAuthentication, UserPermissions
from demo_api.dto.user_registration import UserRegistration
from demo_api.storage.sqla_implementation.tables import UserTable
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
