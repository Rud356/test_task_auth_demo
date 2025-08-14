from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from demo_api.dto import HashingSettings
from demo_api.storage.protocol import ResourceRepository, RolesRepository, UsersRepository
from demo_api.storage.sqla_implementation.resource_repository_sqla import ResourceRepositorySQLA
from demo_api.storage.sqla_implementation.roles_repository_sqla import RolesRepositorySQLA
from demo_api.storage.sqla_implementation.transaction import TransactionSQLA
from demo_api.storage.sqla_implementation.users_repository_sqla import UsersRepositorySQLA
from demo_api.use_cases import ResourceUseCases, RolesUseCases, UserUseCases
from demo_api.utils.config_schema import AppConfig


class AppConfigProvider(Provider):
    """
    Provides application configuration
    """

    def __init__(self, app_config: AppConfig):
        super().__init__()
        self.app_config: AppConfig = app_config

    @provide(scope=Scope.REQUEST)
    def get_app_config(self) -> AppConfig:
        return self.app_config

    @provide(scope=Scope.REQUEST)
    def get_hashing_settings(self, app_config: AppConfig) -> HashingSettings:
        return HashingSettings(
            app_config.security.password_hash_algorithm,
            app_config.security.password_hash_iterations
        )


class DatabaseSQLAReposProvider(Provider):
    def __init__(self, engine: AsyncEngine):
        super().__init__()
        self.engine: AsyncEngine = engine
        self.session_maker: async_sessionmaker[
            AsyncSession
        ] = async_sessionmaker(
            self.engine,
            expire_on_commit=False
        )

    @provide(scope=Scope.REQUEST)
    def get_transaction_manager(self) -> TransactionSQLA:
        return TransactionSQLA(self.session_maker)

    @provide(scope=Scope.REQUEST)
    def get_users_repository(self, transaction: TransactionSQLA) -> UsersRepository:
        return UsersRepositorySQLA(transaction)

    @provide(scope=Scope.REQUEST)
    def get_roles_repository(self, transaction: TransactionSQLA) -> RolesRepository:
        return RolesRepositorySQLA(transaction)

    @provide(scope=Scope.REQUEST)
    def get_resource_repository(self, transaction: TransactionSQLA) -> ResourceRepository:
        return ResourceRepositorySQLA(transaction)


class UseCaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_user_use_case(self, user_repo: UsersRepository) -> UserUseCases:
        return UserUseCases(user_repo)

    @provide(scope=Scope.REQUEST)
    def get_roles_use_case(self, roles_repo: RolesRepository) -> RolesUseCases:
        return RolesUseCases(roles_repo)

    @provide(scope=Scope.REQUEST)
    def get_resource_use_case(self, resource_repo: ResourceRepository) -> ResourceUseCases:
        return ResourceUseCases(resource_repo)
