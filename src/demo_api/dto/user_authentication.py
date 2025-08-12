from pydantic import BaseModel, EmailStr, Field


class UserAuthentication(BaseModel):
    """
    Represents user authentication request information.
    """
    email: EmailStr
    password: str = Field(
        min_length=8, max_length=64,
        pattern=r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,64}$"
    )
