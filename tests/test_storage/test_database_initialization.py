from sqlalchemy import select

from demo_api.storage.sqla_implementation.tables import UserTable
from .fixtures import *


async def test_database_initialized_properly(engine: AsyncEngine, session):
    async with session.begin() as tr:
        await tr.session.execute(select(UserTable).limit(1))
