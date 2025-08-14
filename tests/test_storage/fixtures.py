import secrets

from pathlib import Path
from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio # noqa: enables async mode
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from demo_api.dto import HashingSettings, User, UserPermissions
from demo_api.dto.user_registration import UserRegistration
from demo_api.storage.protocol import ResourceRepository
from demo_api.storage.sqla_implementation.resource_repository_sqla import ResourceRepositorySQLA
from demo_api.storage.sqla_implementation.roles_repository_sqla import RolesRepositorySQLA
from demo_api.storage.sqla_implementation.tables.base_table import BaseTable # noqa: base metadata
import demo_api.storage.sqla_implementation.tables # noqa: filling metadata

from demo_api.storage.sqla_implementation.transaction import TransactionSQLA
from demo_api.storage.sqla_implementation.users_repository_sqla import UsersRepositorySQLA
from demo_api.utils.config_schema import AppConfig, load_config


@pytest.fixture(scope="module")
def config() -> AppConfig:
    return load_config(Path(__file__).parent.parent / "test_config.toml")


@pytest.fixture(scope="module")
def hashing_settings(config: AppConfig) -> HashingSettings:
    return HashingSettings(
        hash_algorithm=config.security.password_hash_algorithm,
        iterations_count=config.security.password_hash_iterations
    )


@pytest.fixture()
async def engine(config: AppConfig) -> AsyncEngine:
    engine: AsyncEngine = create_async_engine(
        config.db_settings.connection_string,
        echo=True
    )

    return engine


@pytest.fixture()
async def session_maker(engine) -> async_sessionmaker[AsyncSession]:
    session_maker: async_sessionmaker[
        AsyncSession
    ] = async_sessionmaker(
        engine,
        expire_on_commit=False
    )

    return session_maker


@pytest.fixture()
async def session(session_maker: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, Any]:
    async with session_maker() as session:
        yield session


@pytest.fixture()
def transaction(session_maker: async_sessionmaker[AsyncSession]) -> TransactionSQLA:
    return TransactionSQLA(session_maker)


@pytest.fixture()
def user_repo(transaction: TransactionSQLA) -> UsersRepositorySQLA:
    return UsersRepositorySQLA(transaction)


@pytest.fixture()
def roles_repo(transaction: TransactionSQLA) -> RolesRepositorySQLA:
    return RolesRepositorySQLA(transaction)


@pytest.fixture()
def resources_repo(transaction: TransactionSQLA) -> ResourceRepositorySQLA:
    return ResourceRepositorySQLA(transaction)


def generate_credentials() -> UserRegistration:
    return UserRegistration(
        email=f"demo_email{secrets.token_urlsafe(16)}@example.com",
        name=f"test_{secrets.token_urlsafe(5)}",
        surname=f"test1_{secrets.token_urlsafe(5)}",
        third_name=f"test2_{secrets.token_urlsafe(5)}",
        password=f"DemoPass12{secrets.token_urlsafe(5)}"
    )

@pytest.fixture()
def user_credentials() -> UserRegistration:
    return generate_credentials()


async def register_user(
    user_repo: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
) -> User:
    resulting_user: User = await user_repo.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )
    assert resulting_user.user_id and resulting_user.is_active

    return resulting_user

@pytest.fixture()
async def new_registered_user(
    user_repo: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
) -> User:
    return await register_user(user_repo, user_credentials, hashing_settings)
