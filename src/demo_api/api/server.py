import uvicorn
from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from starlette.middleware.cors import CORSMiddleware

from demo_api.api.endpoints import (
    api,
    user_resources, # noqa: F401 user for assigning user resource
    business_resources, # noqa: F401 user for assigning business resource
    roles_resources # noqa: F401 user for assigning roles resource
)
from demo_api.utils.config_schema import AppConfig
from demo_api.utils.providers import AppConfigProvider, DatabaseSQLAReposProvider, UseCaseProvider


def setup_app(config: AppConfig) -> FastAPI:
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
    app.include_router(api)

    return app


def main(config: AppConfig) -> None:
    app: FastAPI = setup_app(config)

    uvicorn.run(
        app,
        host=config.host,
        port=config.port
    )
