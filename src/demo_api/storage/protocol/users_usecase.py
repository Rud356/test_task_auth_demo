from abc import abstractmethod
from typing import Protocol, runtime_checkable
from uuid import UUID

from demo_api.dto import HashingSettings, User, UserAuthentication, SessionData, UserDetailed, UserPermissions
from demo_api.dto.user_registration import UserRegistration


@runtime_checkable
class UsersUsecase(Protocol):
    @abstractmethod
    async def login(self, authentication_data: UserAuthentication, hashing_settings: HashingSettings) -> SessionData:
        """
        Authorizes user by provided authentication request data.

        :param authentication_data: Authentication request data.
        :param hashing_settings: Hashing settings for processing password.
        :return: Valid session data.
        :raise ValueError: Invalid authorization data provided.
        :raise NotFoundError: If no such user is registered.
        """
        pass

    @abstractmethod
    async def register_user(
        self, user_data: UserRegistration, permissions: UserPermissions, hashing_settings: HashingSettings
    ) -> User:
        """
        Registers user in database with specified permissions.

        :param user_data: User details who will be registered.
        :param permissions: New users permissions.
        :param hashing_settings: Hashing settings for processing password.
        :return: New user information.
        :raise DataIntegrityError: Registering same account again.
        """

    @abstractmethod
    async def terminate_session(self, session_data: SessionData) -> bool:
        """
        Terminates current user session in database.

        :param session_data: Information about current session.
        :return: Has session been terminated.
        :raise NotFoundError: If session was not found.
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
    ) -> list[UserDetailed]:
        """
        Lists registered users in system.

        :param limit: How many records to fetch.
        :param offset: How many records to skip.
        :param include_deactivated: Specifies if deactivated users are included.
        :return: List of users objects.
        """

    @abstractmethod
    async def get_user(self, user_id: UUID) -> UserDetailed:
        """
        Fetches information about specified user.

        :param user_id: Users identifier.
        :return: User information.
        :raise NotFoundError: If user was not found.
        """

    @abstractmethod
    async def get_user_by_session(self, session_id: str) -> UserDetailed:
        """
        Fetches user by their session information.

        :param session_id: Provided session identifier.
        :return: Information about user.
        :raise NotFoundError: If users session is not found amongst active sessions.
        """

    @abstractmethod
    async def terminate_user(self, user_id: UUID) -> bool:
        """
        Locks out user account and removes all active sessions.

        :param user_id: Users identifier.
        :return: Has user been locked out.
        :raise NotFoundError: If user was not found.
        """
