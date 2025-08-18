from uuid import UUID

from dishka import FromDishka
from fastapi import Depends, HTTPException, Query, Response
from starlette.responses import PlainTextResponse
from typing_extensions import Annotated

from demo_api.api.services import authentication_service
from demo_api.dto import CreateRoleRequest, Role
from demo_api.storage.exceptions import NotFoundError
from demo_api.use_cases import RolesUseCases
from .api_router import api
from ..services.authentication_service import UserAuthenticatedData


@api.get(
    "/roles",
    description="Lists all roles in system",
    tags=["Roles"],
)
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


@api.post(
    "/roles",
    description="Creates new role in system",
    tags=["Roles"],
    status_code=201,
    responses={
        201: {
            "description": "Role successfully created"
        },
        403: {
            "description": "User does not have permissions for adding roles"
        },
    }
)
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


@api.put(
    "/roles/{role_id}",
    description="Edits role in system",
    tags=["Roles"],
    responses={
        200: {
            "description": "Role successfully edited"
        },
        400: {
            "description": "Role ID in path and in body are different"
        },
        403: {
            "description": "User does not have permissions to edit roles"
        },
        404: {
            "description": "Role does not exist for modification"
        }
    }
)
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
        raise HTTPException(status_code=404, detail="Role does not exist for modification")


@api.delete(
    "/roles/{role_id}",
    description="Delete selected role",
    tags=["Roles"],
    responses={
        200: {
            "description": "Role successfully deleted"
        },
        403: {
            "description": "User does not have permissions to edit roles"
        },
        404: {
            "description": "Role does not exist for modification"
        }
    }
)
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


@api.post(
    "/roles/{role_id}/assignments",
    description="Assigns role to a user",
    tags=["Roles", "Permissions"],
    responses={
        200: {
            "description": "Role successfully deleted"
        },
        404: {
            "description": "Role does not exist to be assigned to user or user not found"
        }
    }
)
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
        raise HTTPException(status_code=403, detail="User unauthorized to add roles to users")


@api.delete(
    "/roles/{role_id}/assignments",
    description="Removes role from user",
    tags=["Roles", "Permissions"],
    responses={
        200: {
            "description": "Role successfully removed from user"
        },
        403: {
            "description": "User does not have permissions to remove roles from others"
        },
        404: {
            "description": "Role does not exist to be removed from user or user not found"
        }
    }
)
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
) -> PlainTextResponse:
    try:
        if await roles_use_case.remove_role_from_user(
                user_sessions.user, from_user_id, role_id
        ):
            return PlainTextResponse(content="Ok")

        else:
            raise HTTPException(
                status_code=404,
                detail="Role has not been removed from user since either role or user not found"
            )

    except PermissionError:
        raise HTTPException(status_code=403, detail="User unauthorized to add and remove roles on users")
