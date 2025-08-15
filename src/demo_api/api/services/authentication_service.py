import hashlib
from datetime import datetime, timedelta, timezone

import jwt
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Depends
from pydantic import BaseModel, ValidationError
from typing_extensions import Any

from demo_api.api.exceptions import BadTokenPayload
from demo_api.api.security_definition import cookie_scheme
from demo_api.dto import SessionData, UserDetailed
from demo_api.storage.exceptions import NotFoundError
from demo_api.use_cases import UserUseCases
from demo_api.utils.config_schema import AppConfig


class UserAuthenticatedData(BaseModel):
    user: UserDetailed
    session: SessionData


@inject
async def authenticate_by_session_token(
    app_config: FromDishka[AppConfig],
    user_use_case: FromDishka[UserUseCases],
    session_token: str = Depends(cookie_scheme),
) -> UserAuthenticatedData:
    """
    Authenticates user by supplied token.

    :param app_config: App configuration.
    :param user_use_case: Users use cases.
    :param session_token: Supplied jwt token.
    :return: User data and current session.
    """
    try:
        payload: dict[str, Any] = jwt.decode(
            session_token.lstrip("Bearer "),
            hashlib.sha256(app_config.security.jwt_signing_secret.encode("utf8")).hexdigest(),
            algorithms=["HS256"]
        )
        session: SessionData = SessionData.model_validate(payload)

    except (
        ValidationError,
        jwt.ExpiredSignatureError,
        jwt.exceptions.InvalidSignatureError
    ) as err:
        raise BadTokenPayload() from err

    try:
        return UserAuthenticatedData(
            user=await user_use_case.get_user_by_session(
                session.session_id
            ),
            session=session
        )

    except NotFoundError:
        raise BadTokenPayload()


def encode_user_session_token(
    app_config: AppConfig,
    session_data: SessionData
) -> tuple[str, datetime]:
    """
    Encodes session data as JWT token.

    :param app_config: Application configuration.
    :param session_data: Users token data.
    :return: Encoded token and when it expires.
    """
    time_alive: timedelta = timedelta(
        seconds=app_config.security.access_token_alive_time_in_seconds
    )
    expires_at: datetime = datetime.now(tz=timezone.utc) + time_alive
    return jwt.encode(
        {
            "exp": expires_at,
            **session_data.model_dump()
        },
        hashlib.sha256(app_config.security.jwt_signing_secret.encode("utf8")).hexdigest(),
        algorithm="HS256"
    ), expires_at
