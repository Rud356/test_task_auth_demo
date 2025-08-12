from uuid import UUID

from sqlalchemy import ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from .base_table import BaseTable


class ResourceTable(BaseTable):
    resource_id: Mapped[int] = mapped_column(
        autoincrement=True, primary_key=True
    )
    author_id: Mapped[Uuid[UUID]] = mapped_column(
        ForeignKey("user.user_id")
    )
    content: Mapped[str] = mapped_column(
        Text(length=2048)
    )

    __tablename__ = "resource"
