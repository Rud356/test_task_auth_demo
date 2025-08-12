from .role import Role
from .user import User
from .user_permissions import UserPermissions


class UserDetailed(User):
    roles: list[Role]
    user_permissions: UserPermissions
