from contextlib import AbstractAsyncContextManager
from inspect import Traceback
from typing import Any, Protocol, TypeVar, runtime_checkable

SessionObject = TypeVar("SessionObject", covariant=True)


@runtime_checkable
class TransactionManager(Protocol[SessionObject], AbstractAsyncContextManager[Any]):
    """
    Manages transaction objects for database.
    """

    async def __aenter__(self) -> SessionObject:
        """
        Starts transaction.

        :return: Transaction object.
        """

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
