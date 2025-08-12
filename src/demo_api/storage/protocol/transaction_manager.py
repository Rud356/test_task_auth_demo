from contextlib import AbstractAsyncContextManager
from inspect import Traceback
from typing import Any, Protocol, Self, runtime_checkable


@runtime_checkable
class TransactionManager(Protocol, AbstractAsyncContextManager[Any]):
    """
    Управляет транзакциями и сохранением изменений.
    """

    async def commit(self) -> None:
        """
        Saves changes.

        :return: Nothing.
        """

    async def rollback(self) -> None:
        """
        Rolls back changes.

        :return: Nothing.
        """

    async def start_nested_transaction(self) -> "TransactionManager":
        """
        Starts nested transaction.

        :return: New nested transaction.
        """

    async def __aenter__(self) -> Self:
        """
        Starts transaction.

        :return: Transaction object.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[Exception | Any] | None,
        exc_value: Exception | Any | None,
        traceback: Traceback | Any
    ) -> None:
        """
        Finishes transaction.

        :param exc_type: Exception type.
        :param exc_value: Exception value.
        :param traceback: Traceback.
        :return: Nothing.
        """
        return None
