from dishka import FromDishka
from fastapi import Depends, HTTPException, Query
from pydantic import Field
from typing_extensions import Annotated

from demo_api.api.services import authentication_service
from demo_api.dto import Resource, ResourceDetails, ResourcePermissionsUpdate
from demo_api.storage.exceptions import NotFoundError
from demo_api.use_cases import ResourceUseCases
from .api_router import api
from .dto import ResourcePermissionsModified
from ..services.authentication_service import UserAuthenticatedData


@api.get(
    "/resources",
    description="Fetches a list of resources",
    tags=["Resources"]
)
async def get_list_of_resources(
    user_session: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ],
    resource_use_case: FromDishka[ResourceUseCases],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    list_all: Annotated[bool, Query()] = False
) -> list[ResourceDetails]:
    try:
        if list_all:
            return await resource_use_case.list_all_resources(
                user_session.user,
                limit,
                offset
            )

        else:
            return await resource_use_case.list_available_resources(
                user_session.user,
                limit,
                offset
            )

    except PermissionError:
        raise HTTPException(status_code=403, detail="User can't view all resources")


@api.post(
    "/resources",
    description="Creates a new resource",
    tags=["Resources"],
    status_code=201
)
async def create_resource(
    user_session: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ],
    resource_use_case: FromDishka[ResourceUseCases],
    content: Annotated[str, Field(min_length=1, max_length=2048)]
) -> Resource:
    try:
        return await resource_use_case.create_resource(
            user_session.user,
            content
        )

    except PermissionError:
        raise HTTPException(status_code=403, detail="User can't view all resources")


@api.get(
    "/resources/{resource_id}",
    description="Fetches specific resource",
    tags=["Resources"]
)
async def get_resource_by_id(
    user_session: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ],
    resource_use_case: FromDishka[ResourceUseCases],
    resource_id: int,
) -> ResourceDetails:
    try:
        return await resource_use_case.get_resource_by_id(
            user_session.user,
            resource_id
        )

    except PermissionError:
        raise HTTPException(status_code=403, detail="User can't view this resource")

    except NotFoundError:
        raise HTTPException(status_code=404, detail="Resource was not found")


@api.patch(
    "/resources/{resource_id}",
    description="Edits resource",
    tags=["Resources"]
)
async def edit_resource(
    user_session: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ],
    resource_use_case: FromDishka[ResourceUseCases],
    resource_id: int,
    content: Annotated[str, Field(min_length=1, max_length=2048)]
) -> Resource:
    try:
        return await resource_use_case.edit_resource(
            user_session.user,
            resource_id,
            content
        )

    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="User can't view all resources"
        )

    except NotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Specified resource was not found"
        )


@api.put(
    "/resource/{resource_id}/permissions",
    description="Edits access permissions for roles",
    tags=["Resources", "Permissions"]
)
async def change_resource_access_permissions(
    user_session: Annotated[
        UserAuthenticatedData,
        Depends(
            authentication_service.authenticate_by_session_token
        )
    ],
    resource_use_case: FromDishka[ResourceUseCases],
    resource_id: int,
    resource_permissions: ResourcePermissionsUpdate
) -> ResourcePermissionsModified:
    try:
        if await resource_use_case.set_roles_permissions_on_resource(
            user_session.user,
            resource_id,
            resource_permissions
        ):
            return ResourcePermissionsModified(
                resource_id=resource_id,
                new_permissions=resource_permissions
            )

        else:
            raise HTTPException(
                status_code=400,
                detail="Either role or resource were not found"
            )

    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="User doesn't have permissions to edit resource access permissions"
        )
