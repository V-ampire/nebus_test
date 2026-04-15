from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bootstrap.config.pg import PgConfig
from bootstrap.interfaces import DbSessionFactoryInterface


AsyncSessionType = async_sessionmaker[AsyncSession]


@dataclass
class DbSessionFactory(DbSessionFactoryInterface):
    pg_config: PgConfig

    _engine = None

    def __post_init__(self):
        self._engine = self._init_engine()

    def _init_engine(self):
        return create_async_engine(self.pg_config.async_dsn)

    def get_engine(self):
        return self._engine

    def get_session(self) -> AsyncSessionType:
        return async_sessionmaker(self._engine, expire_on_commit=True)
