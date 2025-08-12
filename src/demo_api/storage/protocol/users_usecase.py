from abc import abstractmethod
from typing import Protocol, runtime_checkable
from uuid import UUID

from demo_api.dto import User, UserAuthentication, SessionData, UserPermissions
from demo_api.dto.user_registration import UserRegistration


@runtime_checkable
class UsersUsecase(Protocol):
    @abstractmethod
    async def login(self, authentication_data: UserAuthentication) -> SessionData:
        """
        Authorizes user by provided authentication request data.

        :param authentication_data: Authentication request data.
        :return: Valid session data.
        :raise ValueError: Invalid authorization data provided.
        """
        pass

    @abstractmethod
    async def register_user(self, user_data: UserRegistration, permissions: UserPermissions) -> User:
        """
        Registers user in database with specified permissions.

        :param user_data: User details who will be registered.
        :param permissions: New users permissions.
        :return: New user information.
        """

    @abstractmethod
    async def terminate_session(self, session_data: SessionData) -> bool:
        """
        Terminates current user session in database.

        :param session_data: Information about current session.
        :return: Has session been terminated.
        """

    @abstractmethod
    async def terminate_all_sessions(self, user_id: UUID) -> bool:
        """
        Terminates all user sessions.

        :param user_id: User whose sessions will be terminated.
        :return: Has sessions been successfully terminated.
        """

    @abstractmethod
    async def list_users(
        self, limit: int = 100, offset: int = 0, include_deactivated: bool = False
    ) -> list[User]:
        """
        Lists registered users in system.

        :param limit: How many records to fetch.
        :param offset: How many records to skip.
        :param include_deactivated: Specifies if deactivated users are included.
        :return: List of users objects.
        """
