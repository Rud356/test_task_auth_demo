import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_table import BaseTable
from .user_table import UserTable


class SessionsTable(BaseTable):
    user_id: Mapped[Uuid[UUID]] = mapped_column(
        ForeignKey("user.user_id"),
        primary_key=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    session_id: Mapped[str] = mapped_column(String(32))
    is_alive: Mapped[bool] = mapped_column(default=True)

    user: Mapped[UserTable] = relationship(
        lazy="joined",
        cascade="all, delete-orphan"
    )

    __tablename__ = "session"
