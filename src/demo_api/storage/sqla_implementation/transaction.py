from inspect import Traceback
from typing import Any, Self

from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction

from demo_api.storage.protocol import TransactionManager


class TransactionSQLA(TransactionManager):
    """
    Manages SQLAlchemy ORM session.
    """

    def __init__(self, session: AsyncSession, transaction: AsyncSessionTransaction):
        self.session: AsyncSession = session
        self.transaction: AsyncSessionTransaction = transaction

    async def start_nested_transaction(self) -> "TransactionSQLA":
        return TransactionSQLA(
            self.session,
            self.session.begin_nested()
        )

    async def commit(self) -> None:
        await self.transaction.commit()

    async def rollback(self) -> None:
        await self.transaction.rollback()

    async def __aenter__(self) -> Self:
        await self.transaction.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[Exception | Any] | None,
        exc_value: Exception | Any | None,
        traceback: Traceback | Any
    ) -> None:
        await self.transaction.__aexit__(exc_type, exc_value, traceback)
        return None
