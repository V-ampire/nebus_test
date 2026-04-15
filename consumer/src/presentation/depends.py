from typing import Annotated

from fast_depends import Depends
from faststream import Context
from sqlalchemy.ext.asyncio import AsyncSession

from bootstrap.interfaces import DbSessionFactoryInterface


async def get_db(di_container=Context()):
    factory = di_container.resolve(DbSessionFactoryInterface)
    async_session = factory.get_session()
    async with async_session() as session:
        yield session


db_session_dep = Annotated[AsyncSession, Depends(get_db)]
