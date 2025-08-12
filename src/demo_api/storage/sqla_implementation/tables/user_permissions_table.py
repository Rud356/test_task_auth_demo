from uuid import UUID

from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from .base_table import BaseTable


class UserPermissionsTable(BaseTable):
    user_id: Mapped[Uuid[UUID]] = mapped_column(
        ForeignKey("user.user_id"),
        primary_key=True
    )
    edit_roles: Mapped[bool]
    view_all_resources: Mapped[bool]
    administrate_users: Mapped[bool]
    administrate_resources: Mapped[bool]

    __tablename__ = "user_permissions"
