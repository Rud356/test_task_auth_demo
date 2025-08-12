from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_table import BaseTable

if TYPE_CHECKING:
    from .assigned_roles_table import AssignedRolesTable

class RolesTable(BaseTable):
    role_id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    role_name: Mapped[str] = mapped_column(String(64))

    assigned_to_users: Mapped[list[AssignedRolesTable]] = relationship(
        lazy="noload",
        cascade="all, delete-orphan",
        back_populates="role"
    )

    __tablename__ = "role"
