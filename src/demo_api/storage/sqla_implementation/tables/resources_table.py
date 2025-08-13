from uuid import UUID

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from .base_table import BaseTable


class ResourceTable(BaseTable):
    resource_id: Mapped[int] = mapped_column(
        autoincrement=True, primary_key=True
    )
    author_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("user.user_id")
    )
    content: Mapped[str] = mapped_column(
        String(2048)
    )

    __tablename__ = "resource"
