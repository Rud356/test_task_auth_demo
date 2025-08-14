from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from starlette.middleware.cors import CORSMiddleware

from demo_api.utils.config_schema import AppConfig
from demo_api.utils.providers import AppConfigProvider, DatabaseSQLAReposProvider, UseCaseProvider


def main(config: AppConfig) -> None:
    app: FastAPI = FastAPI(
        title="Demo API of resource management",
        host=config.host,
        port=config.port
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.security.allowed_cors_domains,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    engine: AsyncEngine = create_async_engine(config.db_settings.connection_string)

    container: AsyncContainer = make_async_container(
        AppConfigProvider(config),
        DatabaseSQLAReposProvider(engine),
        UseCaseProvider()
    )
    setup_dishka(container=container, app=app)

