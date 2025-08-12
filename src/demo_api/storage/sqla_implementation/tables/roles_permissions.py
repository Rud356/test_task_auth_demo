
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base_table import BaseTable


class RolesPermissionsTable(BaseTable):
    role_id: Mapped[int] = mapped_column(
        ForeignKey("role.role_id"),
        autoincrement=True, primary_key=True
    )
    resource_id: Mapped[int] = mapped_column(
        ForeignKey("resource.resource_id"), primary_key=True
    )
    can_view_resource: Mapped[bool]
    can_edit_resource: Mapped[bool]

    __tablename__ = "roles_permissions"
