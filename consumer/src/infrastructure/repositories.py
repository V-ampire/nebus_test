from dataclasses import dataclass
from typing import ClassVar, Type

from pydantic import UUID4
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bootstrap.db.models import PaymentModel
from bootstrap.db.utils import DoesNotExists, get_returning_fields, get_conditions
from core.dto import PaymentDTO


@dataclass
class PaymentRepository:
    model: ClassVar[Type[PaymentModel]] = PaymentModel

    session: AsyncSession

    async def update(self, payment_id: UUID4, update_data: dict) -> PaymentDTO:
        update_query = (
            update(self.model)
            .where(self.model.get_pk() == payment_id)
            .values(**update_data)
            .returning(*get_returning_fields(self.model, PaymentDTO))
        )
        cursor = await self.session.execute(update_query)
        return PaymentDTO(**cursor.mappings().first())

    async def fetch(self, select_for_update: bool = False, **filters) -> PaymentDTO:
        select_query = (
            select(*get_returning_fields(self.model, PaymentDTO))
            .where(*get_conditions(self.model, **filters))
        )
        if select_for_update:
            select_query = select_query.with_for_update(skip_locked=True)
        cursor = await self.session.execute(select_query)
        data = cursor.mappings().first()
        if not data:
            raise DoesNotExists(f"Payment with {filters} does not exist.")

        return PaymentDTO(**data)

