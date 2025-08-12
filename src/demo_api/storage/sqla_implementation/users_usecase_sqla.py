import secrets
from hashlib import pbkdf2_hmac
from typing import Sequence
from uuid import UUID

from sqlalchemy import Select, Update, and_
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import StaleDataError

from demo_api.dto import HashingSettings, Role, SessionData, User, UserAuthentication, UserDetailed, UserPermissions
from demo_api.dto.user_registration import UserRegistration
from demo_api.storage.exceptions import DataIntegrityError, NotFoundError
from demo_api.storage.protocol import UsersUsecase
from demo_api.storage.sqla_implementation.tables import CredentialsTable, SessionsTable, UserPermissionsTable, UserTable
from demo_api.storage.sqla_implementation.transaction import TransactionSQLA


class UsersUsecaseSQLA(UsersUsecase):
    def __init__(self, transaction: TransactionSQLA):
        self.transaction: TransactionSQLA = transaction

    async def login(self, authentication_data: UserAuthentication, hashing_settings: HashingSettings) -> SessionData:
        async with self.transaction as tr:
            query: Select[tuple[UserTable]] = Select(UserTable).join(UserTable.credentials).options(
                joinedload(UserTable.credentials)
            ).where(
                and_(
                    CredentialsTable.email == authentication_data.email,
                    UserTable.is_active.is_(True)
                )
            )

            try:
                user_data: UserTable = (await tr.execute(query)).scalar_one()

            except NoResultFound as err:
                raise NotFoundError() from err

            if user_data.credentials.password is None:
                raise ValueError("User is deactivated")

            hashed_input: str = pbkdf2_hmac(
                hashing_settings.hash_algorithm,
                authentication_data.password.encode("utf-8"),
                user_data.credentials.salt.encode("utf-8"),
                hashing_settings.iterations_count
            ).hex()

            if not secrets.compare_digest(hashed_input, user_data.credentials.password):
                raise ValueError("Invalid password provided")

            new_user_session: SessionsTable = SessionsTable(
                user_id=user_data.user_id,
                session_id=secrets.token_hex(16)
            )
            tr.add(new_user_session)
            await tr.commit()

        return SessionData(
            user_id=new_user_session.user_id,
            created_at=new_user_session.created_at,
            session_id=new_user_session.session_id,
            is_alive=new_user_session.is_alive
        )

    async def register_user(
        self,
        user_data: UserRegistration,
        permissions: UserPermissions,
        hashing_settings: HashingSettings
    ) -> User:
        async with self.transaction as tr:
            salt: str = secrets.token_hex(16)
            new_user: UserTable = UserTable(
                name=user_data.name,
                surname=user_data.surname,
                third_name=user_data.third_name,
                credentials=CredentialsTable(
                    email=user_data.email,
                    password=pbkdf2_hmac(
                        "sha3-256",
                        user_data.password.encode("utf-8"),
                        salt.encode("utf-8"),
                        500_000
                    ).hex(),
                    salt=salt
                ),
                user_permissions=UserPermissionsTable(
                    edit_roles=permissions.edit_roles,
                    view_all_resources=permissions.view_all_resources,
                    administrate_users=permissions.administrate_users,
                    administrate_resources=permissions.administrate_resources
                )
            )

            try:
                tr.add(new_user)
                await tr.commit()

            except IntegrityError as err:
                raise DataIntegrityError(
                    "Most likely already have same account registered"
                ) from err

        return User(
            user_id=new_user.user_id,
            name=new_user.name,
            surname=new_user.surname,
            third_name=new_user.third_name,
            is_active=new_user.is_active
        )

    async def terminate_session(self, session_data: SessionData) -> bool:
        async with self.transaction as tr:
            current_session_query: Select[tuple[SessionsTable]] = Select(SessionData).where(
                SessionsTable.session_id == session_data.session_id
            )

            try:
                current_session: SessionsTable = (
                    await tr.execute(current_session_query)
                ).scalar_one()

            except NoResultFound:
                return False

            current_session.is_alive = False

            try:
                await tr.commit()

            except StaleDataError as err:
                return False

        return not current_session.is_alive

    async def terminate_all_sessions(self, user_id: UUID) -> bool:
        async with self.transaction as tr:
            await tr.execute(
                Update(SessionsTable).where(SessionsTable.user_id == user_id)
                .values(is_alive = False)
            )
            await tr.commit()

        return True

    async def list_users(
        self, limit: int = 100, offset: int = 0, include_deactivated: bool = False
    ) -> list[UserDetailed]:
        query: Select[tuple[UserTable, ...]] = Select(UserTable).options(
            joinedload(UserTable.user_permissions),
            joinedload(UserTable.assigned_roles)
        )

        if not include_deactivated:
            query = query.where(UserTable.credentials.is_active)

        async with self.transaction as tr:
            users: list[UserDetailed] = []
            user_records: Sequence[UserTable] = (await tr.scalars(query)).all()

            for user_record in user_records:
                user_view: UserDetailed = UserDetailed(
                    user_id=user_record.user_id,
                    name=user_record.name,
                    surname=user_record.surname,
                    third_name=user_record.third_name,
                    is_active=user_record.is_active,
                    roles=[
                        Role(role_id=assigned_role.role_id, role_name=assigned_role.role.role_name)
                        for assigned_role in user_record.assigned_roles
                    ],
                    user_permissions=UserPermissions(
                        edit_roles=user_record.user_permissions.edit_roles,
                        view_all_resources=user_record.user_permissions.view_all_resources,
                        administrate_users=user_record.user_permissions.administrate_users,
                        administrate_resources=user_record.user_permissions.administrate_resources,
                    )
                )
                users.append(user_view)

        return users

    async def get_user(self, user_id: UUID) -> UserDetailed:
        query: Select[tuple[UserTable, ...]] = Select(UserTable).options(
            joinedload(UserTable.user_permissions),
            joinedload(UserTable.assigned_roles)
        )

        async with self.transaction as tr:
            user_record: UserTable = (await tr.scalar(query)).one()
            user_view: UserDetailed = UserDetailed(
                user_id=user_record.user_id,
                name=user_record.name,
                surname=user_record.surname,
                third_name=user_record.third_name,
                is_active=user_record.is_active,
                roles=[
                    Role(role_id=assigned_role.role_id, role_name=assigned_role.role.role_name)
                    for assigned_role in user_record.assigned_roles
                ],
                user_permissions=UserPermissions(
                    edit_roles=user_record.user_permissions.edit_roles,
                    view_all_resources=user_record.user_permissions.view_all_resources,
                    administrate_users=user_record.user_permissions.administrate_users,
                    administrate_resources=user_record.user_permissions.administrate_resources,
                )
            )

        return user_view

    async def get_user_by_session(self, session_id: str) -> UserDetailed:
        query: Select[tuple[UserTable]] = Select(UserTable).options(
            joinedload(UserTable.user_permissions),
            joinedload(UserTable.assigned_roles)
        ).join(SessionsTable).where(
            and_(
                SessionsTable.session_id == session_id,
                SessionsTable.is_alive.is_(True)
            )
        )

        async with self.transaction as tr:
            try:
                user_record: UserTable = (await tr.execute(query)).scalar_one()

            except NoResultFound:
                raise NotFoundError("No active session was found with provided ID")

            user_view: UserDetailed = UserDetailed(
                user_id=user_record.user_id,
                name=user_record.name,
                surname=user_record.surname,
                third_name=user_record.third_name,
                is_active=user_record.is_active,
                roles=[
                    Role(role_id=assigned_role.role_id, role_name=assigned_role.role.role_name)
                    for assigned_role in user_record.assigned_roles
                ],
                user_permissions=UserPermissions(
                    edit_roles=user_record.user_permissions.edit_roles,
                    view_all_resources=user_record.user_permissions.view_all_resources,
                    administrate_users=user_record.user_permissions.administrate_users,
                    administrate_resources=user_record.user_permissions.administrate_resources,
                )
            )

        return user_view

    async def terminate_user(self, user_id: UUID) -> bool:
        async with self.transaction as tr:
            user: Update = Update(UserTable).where(
                and_(UserTable.is_active.is_(True), UserTable.user_id == user_id)
            ).values(is_active=False)
            await self.terminate_all_sessions(user_id)

            await tr.commit()

        return True
