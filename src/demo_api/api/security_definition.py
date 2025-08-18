from fastapi import Request
from typing import Optional

from fastapi.security import APIKeyCookie
from starlette.exceptions import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED


class APIKeyCookie401(APIKeyCookie):
    async def __call__(self, request: Request) -> Optional[str]:
        try:
            return await super().__call__(request)

        except HTTPException as err:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=err.detail)


cookie_scheme: APIKeyCookie = APIKeyCookie401(
    name="session", description="Users session token"
)
