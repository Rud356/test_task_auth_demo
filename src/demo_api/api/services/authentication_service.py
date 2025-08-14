from datetime import datetime, timedelta, timezone

import jwt
import hashlib
from dishka import FromDishka
from fastapi import Depends
from pydantic import ValidationError
from typing_extensions import Any

from demo_api.api.exceptions import BadTokenPayload
from demo_api.api.security_definition import cookie_scheme
from demo_api.dto import SessionData, UserDetailed
from demo_api.storage.exceptions import NotFoundError
from demo_api.use_cases import UserUseCases
from demo_api.utils.config_schema import AppConfig


async def authenticate_by_session_token(
    app_config: FromDishka[AppConfig],
    user_use_case: FromDishka[UserUseCases],
    session_token: str = Depends(cookie_scheme),
) -> UserDetailed:
    """
    Authenticates user by supplied token.

    :param app_config: App configuration.
    :param user_use_case: Users use cases.
    :param session_token: Supplied jwt token.
    :return: User data.
    """
    try:
        payload: dict[str, Any] = jwt.decode(
            session_token,
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
        return await user_use_case.get_user_by_session(
            session.session_id
        )

    except NotFoundError:
        raise BadTokenPayload()


def encode_user_session_token(
    app_config: AppConfig,
    session_data: SessionData
) -> str:
    """
    Encodes session data as JWT token.

    :param app_config: Application configuration.
    :param session_data: Users token data.
    :return: Encoded token.
    """
    return jwt.encode(
        {
            "exp": datetime.now(tz=timezone.utc) + timedelta(
                seconds=app_config.security.access_token_alive_time_in_seconds
            ),
            **session_data.model_dump()
        },
        hashlib.sha256(app_config.security.jwt_signing_secret.encode("utf8")).hexdigest(),
        algorithm="HS256"
    )
