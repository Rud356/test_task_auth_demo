from uuid import UUID

from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_table import BaseTable
from .roles_table import RolesTable


class AssignedRolesTable(BaseTable):
    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("user.user_id"),
        primary_key=True
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("role.role_id"),
        primary_key=True
    )

    role: Mapped["RolesTable"] = relationship(
        lazy="joined"
    )

    __tablename__ = "assigned_roles"
