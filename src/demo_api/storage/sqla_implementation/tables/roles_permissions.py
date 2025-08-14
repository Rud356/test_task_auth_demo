from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_table import BaseTable

if TYPE_CHECKING:
    from .resources_table import ResourceTable
    from .roles_table import RolesTable


class RolesPermissionsTable(BaseTable):
    role_id: Mapped[int] = mapped_column(
        ForeignKey("role.role_id", ondelete="CASCADE"),
        autoincrement=True, primary_key=True
    )
    resource_id: Mapped[int] = mapped_column(
        ForeignKey("resource.resource_id"), primary_key=True
    )
    can_view_resource: Mapped[bool]
    can_edit_resource: Mapped[bool]

    role: Mapped[RolesTable] = relationship(
        lazy="joined",
        back_populates="resources_permissions"
    )
    resource: Mapped[ResourceTable] = relationship(
        lazy="raise",
        back_populates="roles_permissions"
    )

    __tablename__ = "roles_permissions"
