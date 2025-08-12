import tomllib
from pathlib import Path

from pydantic import BaseModel, Field


class DbSettings(BaseModel):
    connection_string: str


class Security(BaseModel):
    password_hash_algorithm: str
    password_hash_iterations: int = Field(ge=1000, lt=1_000_000)
    jwt_signing_secret: str
    access_token_alive_time_in_seconds: int = Field(ge=600)


class AppConfig(BaseModel):
    host: str
    port: int = Field(ge=1, le=65_535)
    db_settings: DbSettings
    security: Security


def load_config(path: Path) -> AppConfig:
    with path.open(mode='rb') as f:
        return AppConfig(**tomllib.load(f))
