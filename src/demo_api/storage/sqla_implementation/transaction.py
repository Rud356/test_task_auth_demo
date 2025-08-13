from inspect import Traceback
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from demo_api.storage.protocol import TransactionManager


class TransactionSQLA(TransactionManager[AsyncSession]):
    """
    Manages SQLAlchemy ORM session.
    """

    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self.sessionmaker: async_sessionmaker[AsyncSession] = sessionmaker
        self.current_session: AsyncSession | None = None

    async def __aenter__(self) -> AsyncSession:
        self.current_session = self.sessionmaker()

        return self.current_session

    async def __aexit__(
        self,
        exc_type: type[Exception | Any] | None,
        exc_value: Exception | Any | None,
        traceback: Traceback | Any
    ) -> None:
        if self.current_session is not None:
            await self.current_session.close()
        return None
