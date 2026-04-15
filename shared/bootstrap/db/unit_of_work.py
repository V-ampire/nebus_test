from dataclasses import dataclass
from logging import getLogger

from sqlalchemy.ext.asyncio import AsyncSession

from bootstrap.utils import str_exception


logger = getLogger(__name__)


@dataclass
class UnitOfWork:
    session: AsyncSession

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        try:
            if exc:
                error_message = str_exception(exc, with_traceback=True)
                logger.error(error_message)
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            await self.session.close()
