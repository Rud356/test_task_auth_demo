from pathlib import Path
from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio # noqa: enables async mode
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from demo_api.dto import HashingSettings
from demo_api.storage.sqla_implementation.tables.base_table import BaseTable # noqa: base metadata
import demo_api.storage.sqla_implementation.tables # noqa: filling metadata

from demo_api.storage.sqla_implementation.transaction import TransactionSQLA
from demo_api.utils.config_schema import AppConfig, load_config


@pytest.fixture(scope="module")
def config() -> AppConfig:
    return load_config(Path(__file__).parent.parent / "test_config.toml")


@pytest.fixture()
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
