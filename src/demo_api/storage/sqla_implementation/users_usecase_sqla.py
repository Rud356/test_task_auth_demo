import secrets
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload

from demo_api.dto import SessionData, User, UserAuthentication, UserDetailed, UserPermissions
from demo_api.dto.user_registration import UserRegistration
from demo_api.storage.exceptions import NotFoundError
from demo_api.storage.protocol import UsersUsecase
from demo_api.storage.sqla_implementation.tables import UserTable, SessionsTable
from demo_api.storage.sqla_implementation.transaction import TransactionSQLA


class UsersUsecaseSQLA(UsersUsecase):
    def __init__(self, transaction: TransactionSQLA):
        self.transaction: TransactionSQLA = transaction

    async def login(self, authentication_data: UserAuthentication) -> SessionData:
        async with self.transaction as tr:
            query: Select[tuple[UserTable]] = Select(UserTable).options(joinedload(UserTable.credentials)).where(
                UserTable.credentials.email == authentication_data.email
            )

            try:
                user_data: UserTable = (await self.transaction.session.execute(query)).scalar_one()

            except NoResultFound as err:
                raise NotFoundError() from err

            new_user_session: SessionsTable = SessionsTable(
                user_id=user_data.user_id,
                session_id=secrets.token_urlsafe(32)
            )
            await tr.commit()

        return SessionData(
            user_id=new_user_session.user_id.native,
            created_at=new_user_session.created_at,
            session_id=new_user_session.session_id,
            is_alive=new_user_session.is_alive
        )

    async def register_user(self, user_data: UserRegistration, permissions: UserPermissions) -> User:
        pass

    async def terminate_session(self, session_data: SessionData) -> bool:
        pass

    async def terminate_all_sessions(self, user_id: UUID) -> bool:
        pass

    async def list_users(self, limit: int = 100, offset: int = 0, include_deactivated: bool = False) -> list[
        UserDetailed]:
        pass

    async def get_user(self, user_id: UUID) -> UserDetailed:
        pass

    async def get_user_by_session(self, session_data: SessionData) -> UserDetailed:
        pass

    async def terminate_user(self, user_id: UUID) -> bool:
        pass