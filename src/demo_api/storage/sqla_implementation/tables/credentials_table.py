from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from .base_table import BaseTable


class CredentialsTable(BaseTable):
    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("user.user_id"),
        primary_key=True
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True, index=True, nullable=False
    )
    password: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True
    )
    salt: Mapped[str] = mapped_column(String(32))
    is_active: Mapped[bool] = mapped_column(default=True)

    __tablename__ = "credentials"
