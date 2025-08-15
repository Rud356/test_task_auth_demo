from dishka import FromDishka
from fastapi import Depends, HTTPException, Response
from typing_extensions import Annotated

from demo_api.api.services import authentication_service
from demo_api.dto import HashingSettings, SessionData, UserAuthentication
from demo_api.storage.exceptions import NotFoundError
from demo_api.use_cases import UserUseCases
from demo_api.utils.config_schema import AppConfig
from .api_router import api
from ..services.authentication_service import UserAuthenticatedData


@api.post("/login")
async def authenticate_user(
    user_use_case: FromDishka[UserUseCases],
    app_config: FromDishka[AppConfig],
    hashing_settings: FromDishka[HashingSettings],
    request_body: UserAuthentication
) -> Response:

    try:
        session: SessionData = await user_use_case.login(
            request_body,
            hashing_settings
        )

    except NotFoundError:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    response: Response = Response(status_code=200, content="Ok")
    token, expires_at = authentication_service.encode_user_session_token(app_config, session)
    response.set_cookie(
        "session",
        f"Bearer {token}",
        secure=True,
        httponly=True,
        expires=expires_at
    )

    return response



@api.post("/logout")
async def logout_user(
    user_use_case: FromDishka[UserUseCases],
    user_session_data: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ]
) -> Response:
    if await user_use_case.terminate_session(user_session_data.session):
        response: Response = Response(status_code=200, content="Ok")

    else:
        response = Response(status_code=400, content="Session has been terminated before")

    response.delete_cookie("session")
    return response
