from pydantic import Field, model_validator

from .user_registration import UserRegistration


class UserRegistrationForm(UserRegistration):
    password_again: str = Field(
        min_length=8, max_length=64
    )

    @model_validator(mode='after')
    def check_passwords_equality(self) -> "UserRegistrationForm":
        if self.password != self.password_again:
            raise ValueError("Password fields must be equal")

        return self
