import uuid
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .assigned_roles_table import AssignedRolesTable
from .base_table import BaseTable
from .credentials_table import CredentialsTable
from .user_permissions_table import UserPermissionsTable


class UserTable(BaseTable):
    user_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(
        String(255)
    )
    surname: Mapped[str] = mapped_column(
        String(255)
    )
    third_name: Mapped[Optional[str]] = mapped_column(
        String(255)
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    credentials: Mapped[CredentialsTable] = relationship(
        lazy="raise",
        cascade="all, delete-orphan"
    )
    user_permissions: Mapped[UserPermissionsTable] = relationship(
        lazy="joined",
        cascade="all, delete-orphan"
    )
    assigned_roles: Mapped[list[AssignedRolesTable]] = relationship(
        lazy="raise",
        cascade="all, delete-orphan"
    )

    __tablename__ = "user"
