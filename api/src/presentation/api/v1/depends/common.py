from fastapi import Depends, Request

from typing import Type, Annotated, AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from bootstrap.interfaces import DbSessionFactoryInterface
from bootstrap.db.unit_of_work import UnitOfWork
from infrastructure.di import DIContainer


def get_di_container(request: Request):
    return request.state.di_container


di_container_dep = Annotated[DIContainer, Depends(get_di_container)]


async def get_db(di_container: di_container_dep):
    factory = di_container.resolve(DbSessionFactoryInterface)
    async_session = factory.get_session()
    async with async_session() as session:
        yield session


db_session_dep = Annotated[AsyncSession, Depends(get_db)]


async def get_unit_of_work(session: db_session_dep) -> AsyncIterator[UnitOfWork]:
    async with UnitOfWork(session) as uow:
        yield uow


unit_of_work_dep = Annotated[UnitOfWork, Depends(get_unit_of_work)]


class CQRSDependency:
    def __init__(self, resolve_cls: Type):
        self.resolve_cls = resolve_cls


class CommandDependency(CQRSDependency):

    def __call__(
        self,
        uow: unit_of_work_dep,
        di_container: di_container_dep
    ):
        return di_container.resolve(
            self.resolve_cls,
            depends={AsyncSession: uow.session},
        )

class QueryDependency(CQRSDependency):

    def __call__(
        self,
        session: db_session_dep,
        di_container: di_container_dep
    ):
        return di_container.resolve(
            self.resolve_cls,
            depends={AsyncSession: session},
        )

