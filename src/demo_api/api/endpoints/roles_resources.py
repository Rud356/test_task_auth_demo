from uuid import UUID

from dishka import FromDishka
from fastapi import Depends, HTTPException, Query, Response
from typing_extensions import Annotated

from demo_api.api.services import authentication_service
from demo_api.dto import CreateRoleRequest, Role
from demo_api.storage.exceptions import NotFoundError
from demo_api.use_cases import RolesUseCases
from .api_router import api
from ..services.authentication_service import UserAuthenticatedData


@api.get("/roles")
async def get_all_roles(
    _: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ],
    roles_use_case: FromDishka[RolesUseCases]
) -> list[Role]:
    return await roles_use_case.list_roles()


@api.post("/roles")
async def create_role(
    user_sessions: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ],
    roles_use_case: FromDishka[RolesUseCases],
    role: CreateRoleRequest
) -> Role:
    try:
        return await roles_use_case.create_role(
            user_sessions.user, role
        )

    except PermissionError:
        raise HTTPException(status_code=403, detail="User unauthorized to add roles")

    except NotFoundError:
        raise HTTPException(status_code=404, detail="Role does not exist for modification")


@api.put("/roles/{role_id}")
async def update_role(
    user_sessions: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ],
    roles_use_case: FromDishka[RolesUseCases],
    role_id: int,
    updated_role: Role
) -> Role:
    if role_id != updated_role.role_id:
        raise HTTPException(status_code=400, detail="Role ids must match")

    try:
        return await roles_use_case.update_role(
            user_sessions.user, updated_role
        )

    except PermissionError:
        raise HTTPException(status_code=403, detail="User unauthorized to add roles")

    except NotFoundError:
        raise HTTPException(status_code=404, detail="Role does not exist for deletion")

@api.delete("/roles/{role_id}")
async def delete_role(
    user_sessions: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ],
    roles_use_case: FromDishka[RolesUseCases],
    role_id: int
) -> bool:
    try:
        return await roles_use_case.delete_role(
            user_sessions.user, role_id
        )

    except PermissionError:
        raise HTTPException(status_code=403, detail="User unauthorized to add roles")

    except NotFoundError:
        raise HTTPException(status_code=404, detail="Role does not exist for deletion")


@api.post("/roles/{role_id}/assignments")
async def assign_user_a_role(
    user_sessions: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ],
    roles_use_case: FromDishka[RolesUseCases],
    role_id: int,
    to_user_id: Annotated[UUID, Query()]
) -> Response:
    try:
        if await roles_use_case.assign_role_to_user(
            user_sessions.user, to_user_id, role_id
        ):
            return Response(content="Ok")

        else:
            raise HTTPException(
                status_code=404,
                detail="User was not assigned a role since either role or user not found"
            )

    except PermissionError:
        raise HTTPException(status_code=403, detail="User unauthorized to add roles")


@api.delete("/roles/{role_id}/assignments")
async def remove_role_from_user(
    user_sessions: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ],
    roles_use_case: FromDishka[RolesUseCases],
    role_id: int,
    from_user_id: Annotated[UUID, Query()]
) -> Response:
    try:
        if await roles_use_case.remove_role_from_user(
                user_sessions.user, from_user_id, role_id
        ):
            return Response(content="Ok")

        else:
            raise HTTPException(
                status_code=404,
                detail="Role has not been removed from user since either role or user not found"
            )

    except PermissionError:
        raise HTTPException(status_code=403, detail="User unauthorized to add roles")
