from uuid import UUID

from dishka import FromDishka
from fastapi import Depends, HTTPException, Query, Response
from starlette.responses import PlainTextResponse
from typing_extensions import Annotated

from demo_api.api.services import authentication_service
from demo_api.dto import (
    HashingSettings,
    PasswordUpdate, SessionData,
    SessionTerminationConfirmed,
    User, UserAuthentication,
    UserDetailed, UserPermissions, UserRegistrationForm,
)
from demo_api.dto import UserUpdate
from demo_api.storage.exceptions import DataIntegrityError, NotFoundError
from demo_api.use_cases import UserUseCases
from demo_api.utils.config_schema import AppConfig
from .api_router import api
from .dto import UserChangedPassword, UserTerminated
from ..services.authentication_service import UserAuthenticatedData



@api.get(
    "/users",
    description="Fetches list of users",
    tags=["Administrative", "User"]
)
async def get_users(
    user_use_case: FromDishka[UserUseCases],
    user_session_data: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ],
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    include_deactivated: Annotated[bool, Query()] = False
) -> list[UserDetailed]:
    try:
        return await user_use_case.list_users(
            user_session_data.user,
            limit, offset, include_deactivated
        )

    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="User does not have permissions to view all users"
        )


@api.get(
    "/users/me",
    description="Fetches current user",
    tags=["User"]
)
async def get_current_user(
    user_session_data: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ]
) -> UserDetailed:
    return user_session_data.user


@api.get(
    "/users/{user_id}",
    description="Fetches user by their ID",
    tags=["User"]
)
async def get_user_by_id(
    user_use_case: FromDishka[UserUseCases],
    user_id: UUID,
    _: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ]
) -> UserDetailed:
    try:
        return await user_use_case.get_user(user_id)

    except NotFoundError:
        raise HTTPException(
            status_code=404,
            detail="User with provided ID not found"
        )


@api.post(
    "/login",
    description="Authenticates user",
    tags=["Account management", "User"]
)
async def authenticate_user(
    user_use_case: FromDishka[UserUseCases],
    app_config: FromDishka[AppConfig],
    hashing_settings: FromDishka[HashingSettings],
    request_body: UserAuthentication
) -> PlainTextResponse:
    try:
        session: SessionData = await user_use_case.login(
            request_body,
            hashing_settings
        )

    except NotFoundError:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    response: PlainTextResponse = PlainTextResponse(status_code=200, content="Ok")
    token, expires_at = authentication_service.encode_user_session_token(app_config, session)
    response.set_cookie(
        "session",
        f"Bearer {token}",
        secure=True,
        httponly=True,
        expires=expires_at
    )

    return response


@api.post(
    "/logout",
    description="Deauthenticates user from system",
    tags=["Account management", "User"]
)
async def logout_user(
    user_use_case: FromDishka[UserUseCases],
    user_session_data: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ]
) -> PlainTextResponse:
    if await user_use_case.terminate_session(user_session_data.session):
        response: PlainTextResponse = PlainTextResponse(status_code=200, content="Ok")

    else:
        response = PlainTextResponse(status_code=400, content="Session has been terminated before")

    response.delete_cookie("session")
    return response


@api.post(
    "/register",
    description="Registers new account",
    status_code=201,
    tags=["Account management", "User"]
)
async def register_user(
    user_use_case: FromDishka[UserUseCases],
    hashing_settings: FromDishka[HashingSettings],
    user_data: UserRegistrationForm
) -> User:
    try:
        return await user_use_case.register_user(user_data, hashing_settings)

    except DataIntegrityError:
        raise HTTPException(status_code=400, detail="User with provided email is already registered")


@api.post(
    "/users/create_new",
    description="Creates new user",
    status_code=201,
    tags=["Account management", "Administrative"]
)
async def create_new_user(
    user_use_case: FromDishka[UserUseCases],
    hashing_settings: FromDishka[HashingSettings],
    user_data: UserRegistrationForm,
    permissions: UserPermissions,
    user_session_data: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ]
) -> User:
    try:
        return await user_use_case.create_new_user(
            user_session_data.user,
            user_data,
            permissions,
            hashing_settings
        )

    except DataIntegrityError:
        raise HTTPException(
            status_code=400,
            detail="User with provided email is already registered"
        )

    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="User doesn't have enough permissions to create other users"
        )

@api.delete(
    "/sessions",
    description="Terminates all current users sessions",
    tags=["Account management", "User"]
)
async def terminate_all_current_users_sessions(
    user_use_case: FromDishka[UserUseCases],
    user_session_data: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ]
) -> SessionTerminationConfirmed:
    try:
        await user_use_case.terminate_all_session(
            user_session_data.user,
            user_session_data.user.user_id
        )
        return SessionTerminationConfirmed(
            user_id=user_session_data.user.user_id,
            terminated=True
        )

    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="Doesn't have permissions to execute action"
        )


@api.delete(
    "/sessions/current",
    description="Terminates only current session",
    tags=["Account management", "User"]
)
async def terminate_current_session(
    user_use_case: FromDishka[UserUseCases],
    user_session_data: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ]
) -> SessionTerminationConfirmed:
    try:
        await user_use_case.terminate_session(
            user_session_data.session
        )
        return SessionTerminationConfirmed(
            user_id=user_session_data.user.user_id,
            terminated=True
        )

    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="Doesn't have permissions to execute action"
        )


@api.delete(
    "/user/{user_id}/sessions",
    description="Terminates all sessions of a specified user",
    tags=["Account management", "User", "Administrative"]
)
async def terminate_all_user_sessions(
    user_use_case: FromDishka[UserUseCases],
    user_id: UUID,
    user_session_data: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ]
) -> SessionTerminationConfirmed:
    try:
        await user_use_case.terminate_all_session(
            user_session_data.user,
            user_id
        )
        return SessionTerminationConfirmed(
            user_id=user_session_data.user.user_id,
            terminated=True
        )

    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="Doesn't have permissions to execute action"
        )


@api.patch(
    "/users/{user_id}",
    description="Changes information about specified user",
    tags=["Account management", "User"]
)
async def update_user_by_id(
    user_use_case: FromDishka[UserUseCases],
    user_id: UUID,
    user_details: UserUpdate,
    user_session_data: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ]
) -> UserDetailed:
    if user_id != user_details.user_id:
        raise HTTPException(
            status_code=400,
            detail="Mismatched IDs of user to update"
        )

    try:
        return await user_use_case.update_user_details(
            user_session_data.user,
            user_details
        )

    except NotFoundError:
        raise HTTPException(
            status_code=404,
            detail="User with provided ID not found"
        )


@api.delete(
    "/users/{user_id}",
    description="Terminates specified user",
    tags=["Account management", "Administrative", "User"]
)
async def terminate_user(
    user_use_case: FromDishka[UserUseCases],
    user_id: UUID,
    user_session_data: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ]
) -> UserTerminated:
    try:
        if await user_use_case.terminate_user(
            user_session_data.user,
            user_id
        ):
            return UserTerminated(
                user_id=user_id,
                is_active=False
            )

        else:
            raise HTTPException(
                status_code=400,
                detail="User is likely already terminated"
            )

    except NotFoundError:
        raise HTTPException(
            status_code=404,
            detail="User with provided ID not found"
        )

    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="User doesn't have permissions to execute termination of other user"
        )


@api.put(
    "/users/{user_id}/password",
    description="Changes password of a specified user",
    tags=["Account management", "User"]
)
async def update_users_password(
    user_use_case: FromDishka[UserUseCases],
    user_id: UUID,
    user_new_password: PasswordUpdate,
    hashing_settings: FromDishka[HashingSettings],
    user_session_data: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ]
) -> UserChangedPassword:
    try:
        has_changed: bool = await user_use_case.change_user_password(
            user_session_data.user,
            user_id,
            user_new_password.password_updated_value,
            hashing_settings
        )
        return UserChangedPassword(
            user_id=user_id,
            changed_password=has_changed
        )

    except NotFoundError:
        raise HTTPException(
            status_code=404,
            detail="User with provided ID not found"
        )

    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="User is not allowed to change other users password"
        )
