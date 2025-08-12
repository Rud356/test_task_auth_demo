from pathlib import Path
from typing import Any, AsyncGenerator

import pytest_asyncio
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from demo_api.storage.sqla_implementation.tables.base_table import BaseTable
import demo_api.storage.sqla_implementation.tables

from demo_api.storage.sqla_implementation.transaction import TransactionSQLA
from demo_api.utils.config_schema import AppConfig, load_config


@pytest.fixture(scope="module")
def config() -> AppConfig:
    return load_config(Path(__file__).parent.parent / "test_config.toml")


@pytest.fixture(scope="module")
async def engine(config: AppConfig) -> AsyncEngine:
    engine: AsyncEngine = create_async_engine(
        config.db_settings.connection_string,
        echo=True
    )

    return engine


@pytest.fixture(scope="module")
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
async def transaction(session: AsyncSession) -> AsyncGenerator[TransactionSQLA, Any]:
    async with session.begin() as transaction:
        yield TransactionSQLA(session, transaction)

    await session.close()
