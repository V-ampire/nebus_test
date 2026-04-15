from dataclasses import dataclass
from typing import ClassVar, Type

from pydantic import UUID4
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bootstrap.db.models import OutboxModel
from bootstrap.db.utils import get_returning_fields, get_conditions, DoesNotExists
from dto import OutboxDTO


@dataclass
class OutboxRepository:
    model: ClassVar[Type[OutboxModel]] = OutboxModel

    session: AsyncSession

    async def fetch_many(self, select_for_update: bool = False, **filters) -> list[OutboxDTO]:
        select_query = (
            select(*get_returning_fields(self.model, OutboxDTO))
            .where(*get_conditions(self.model, **filters))
        )
        if select_for_update:
            select_query = select_query.with_for_update(skip_locked=True)
        cursor = await self.session.execute(select_query)
        return [OutboxDTO(**row) for row in cursor.mappings().all()]

    async def update(self, event_id: UUID4, update_data: dict):
        update_query = (
            update(self.model)
            .where(self.model.get_pk() == event_id)
            .values(**update_data)
        )
        await self.session.execute(update_query)
