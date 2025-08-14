from uuid import UUID

from demo_api.dto import HashingSettings, SessionData, User, UserAuthentication, UserDetailed, UserPermissions
from demo_api.dto.user_registration import UserRegistration
from demo_api.dto.user_update import UserUpdate
from demo_api.storage.protocol import UsersRepository


class UserUseCases:
    def __init__(self, user_repo: UsersRepository):
        self.user_repo: UsersRepository = user_repo

    async def register_user(
        self,
        user_data: UserRegistration,
        hashing_settings: HashingSettings
    ) -> User:
        """
        Registers user in database with default permissions.

        :param user_data: User details who will be registered.
        :param permissions: New users permissions.
        :param hashing_settings: Hashing settings for processing password.
        :return: New user information.
        :raise DataIntegrityError: Registering same account again.
        """
        return await self.user_repo.register_user(
            user_data,
            # Create user with default permissions
            UserPermissions(),
            hashing_settings
        )

    async def create_new_user(
        self,
        created_by: UserDetailed,
        user_data: UserRegistration,
        permissions: UserPermissions,
        hashing_settings: HashingSettings
    ) -> User:
        """
        Registers user in database with specified permissions.

        :param created_by: User that requests creation of a new user.
        :param user_data: User details who will be registered.
        :param permissions: New users permissions.
        :param hashing_settings: Hashing settings for processing password.
        :return: New user information.
        :raise DataIntegrityError: Registering same account again.
        :raise PermissionError: If user tries to give permission that he does not have to another user.
        """
        if not created_by.user_permissions.administrate_users:
            raise PermissionError("User can't create other users with different permissions")

        if not created_by.user_permissions.administrate_users and permissions.administrate_users:
            raise PermissionError("Can't give other user permissions not given to current one")

        if not created_by.user_permissions.view_all_resources and permissions.view_all_resources:
            raise PermissionError("Can't give other user permissions not given to current one")

        if not created_by.user_permissions.edit_roles and permissions.edit_roles:
            raise PermissionError("Can't give other user permissions not given to current one")

        if not created_by.user_permissions.administrate_resources and permissions.administrate_resources:
            raise PermissionError("Can't give other user permissions not given to current one")

        return await self.user_repo.register_user(
            user_data,
            # Create user with default permissions
            permissions,
            hashing_settings
        )

    async def login(
        self,
        authentication_data: UserAuthentication,
        hashing_settings: HashingSettings
    ) -> SessionData:
        """
        Authorizes user by provided authentication request data.

        :param authentication_data: Authentication request data.
        :param hashing_settings: Hashing settings for processing password.
        :return: Valid session data.
        :raise ValueError: Invalid authorization data provided.
        :raise NotFoundError: If no such user is registered.
        """
        return await self.login(
            authentication_data,
            hashing_settings
        )

    async def terminate_session(
        self, session_data: SessionData
    ) -> bool:
        """
        Terminates current user session in database.

        :param session_data: Information about current session.
        :return: Has session been terminated.
        :raise NotFoundError: If session was not found.
        """
        return await self.user_repo.terminate_session(session_data)

    async def terminate_all_session(self, requested_by: UserDetailed, terminate_on_user_id: UUID) -> bool:
        """
        Terminates all user sessions.

        :param requested_by: User who initiates termination.
        :param terminate_on_user_id: User whose sessions will be terminated.
        :return: Has sessions been successfully terminated.
        :raises PermissionError: If user requesting termination of all sessions don't have permissions.
        """
        if requested_by.user_id == terminate_on_user_id:
            return await self.user_repo.terminate_all_sessions(terminate_on_user_id)

        elif requested_by.user_permissions.administrate_users:
            return await self.user_repo.terminate_all_sessions(terminate_on_user_id)

        else:
            raise PermissionError(
                f"User {requested_by.user_id} can't terminate sessions of user {terminate_on_user_id}"
            )

    async def list_users(
        self,
        requested_by: UserDetailed,
        limit: int = 100,
        offset: int = 0,
        include_deactivated: bool = False
    ) -> list[UserDetailed]:
        """
        Lists registered users in system.

        :param requested_by: Who requests viewing a list of users.
        :param limit: How many records to fetch.
        :param offset: How many records to skip.
        :param include_deactivated: Specifies if deactivated users are included.
        :return: List of users objects.
        :raises PermissionError: If user has not been authorized to administrate users.
        """
        if not requested_by.user_permissions.administrate_users:
            raise PermissionError(f"User {requested_by.user_id} can't view all users")

        return await self.user_repo.list_users(limit, offset, include_deactivated)

    async def get_user(self, user_id: UUID) -> UserDetailed:
        """
        Fetches information about specified user.

        :param user_id: Users identifier.
        :return: User information.
        :raise NotFoundError: If user was not found.
        """
        return await self.user_repo.get_user(user_id)

    async def get_user_by_session(self, session_id: str) -> UserDetailed:
        """
        Fetches user by their session information.

        :param session_id: Provided session identifier.
        :return: Information about user.
        :raise NotFoundError: If users session is not found amongst active sessions.
        """
        return await self.user_repo.get_user_by_session(session_id)

    async def terminate_user(self, requested_by: UserDetailed, user_id: UUID) -> bool:
        """
        Locks out user account and removes all active sessions.

        :param requested_by: User who requests termination of a user.
        :param user_id: Users identifier of someone, who will be terminated.
        :return: Has user been locked out.
        :raise NotFoundError: If user was not found.
        :raise PermissionError: If user was not authorized to perform termination.
        """
        if requested_by.user_id == user_id:
            return await self.user_repo.terminate_user(user_id)

        elif requested_by.user_permissions.administrate_users:
            return await self.user_repo.terminate_user(user_id)

        else:
            raise PermissionError(
                f"User {requested_by.user_id} can't terminate user {user_id}"
            )

    async def update_user_details(self, requested_by: UserDetailed, user_details: UserUpdate) -> UserDetailed:
        """
        Updates general information about user.

        :param requested_by: User who requests update of details for a user.
        :param user_details: User information to update.
        :return: Updated details.
        :raise NotFoundError: If user was not found.
        :raise PermissionError: If user was not authorized to perform details update.
        """
        if requested_by.user_id == user_details.user_id:
            return await self.user_repo.update_user_details(user_details)

        elif requested_by.user_permissions.administrate_users:
            return await self.user_repo.update_user_details(user_details)

        else:
            raise PermissionError(
                f"User {requested_by.user_id} can't update details of user {user_details.user_id}"
            )

    async def change_user_password(
        self,
        requested_by: UserDetailed,
        user_id: UUID,
        new_password: str,
        hashing_settings: HashingSettings
    ) -> bool:
        """
        Changes user password to a new one with reset of all sessions.

        :param requested_by: User who requests update of a password for user.
        :param user_id: User to update.
        :param new_password: New password to set for user.
        :param hashing_settings: Settings for hashing a password.
        :return: Flag indicating if password has been changes.
        :raise NotFoundError: If user is not found in database.
        :raise PermissionError: If user can't update password.
        """
        if requested_by.user_id == user_id:
            return await self.user_repo.change_user_password(
                user_id, new_password, hashing_settings
            )

        elif requested_by.user_permissions.administrate_users:
            return await self.user_repo.change_user_password(
                user_id, new_password, hashing_settings
            )

        else:
            raise PermissionError(
                f"User {requested_by.user_id} can't update password of user {user_id}"
            )
