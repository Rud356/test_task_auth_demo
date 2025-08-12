from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base_table import BaseTable


class RolesTable(BaseTable):
    role_id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    role_name: Mapped[str] = mapped_column(String(64))

    __tablename__ = "role"
