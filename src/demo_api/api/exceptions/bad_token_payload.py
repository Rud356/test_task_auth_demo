from fastapi import HTTPException



class BadTokenPayload(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            detail="User did not provide required token",
            status_code=401
        )
