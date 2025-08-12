from uuid import UUID

from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_table import BaseTable
from .roles_table import RolesTable


class AssignedRolesTable(BaseTable):
    user_id: Mapped[Uuid[UUID]] = mapped_column(
        ForeignKey("user.user_id"),
        primary_key=True
    )
    role_id: Mapped[int] = mapped_column(primary_key=True)

    role: Mapped["RolesTable"] = relationship(
        lazy="joined",
        cascade="all, delete-orphan"
    )

    __tablename__ = "assigned_roles"
