from dataclasses import dataclass
from typing import ClassVar, Type

from sqlalchemy import select, column
from sqlalchemy.dialects.postgresql import insert as pg_insert

from sqlalchemy.ext.asyncio import AsyncSession

from bootstrap.db.utils import DoesNotExists, get_conditions, get_returning_fields
from core.dto import CreatePaymentDTO, PaymentDTO, OutboxDTO, CreateOutboxDTO
from bootstrap.db.models import PaymentModel, OutboxModel


@dataclass
class PaymentRepository:
    model: ClassVar[Type[PaymentModel]] = PaymentModel

    session: AsyncSession

    async def fetch(self, **filters) -> PaymentDTO:
        select_query = (
            select(*get_returning_fields(self.model, PaymentDTO))
            .where(*get_conditions(self.model, **filters))
        )
        cursor = await self.session.execute(select_query)
        data = cursor.mappings().first()
        if not data:
            raise DoesNotExists(f"Payment with {filters} does not exist.")

        return PaymentDTO(**data)

    async def create_with_idempotency(self, create_dto: CreatePaymentDTO) -> tuple[bool, PaymentDTO]:
        xmax = column('xmax')
        returning_fields = get_returning_fields(self.model, PaymentDTO)
        returning_fields.append((xmax == 0).label('is_created'))

        insert_query = (
            pg_insert(self.model)
            .on_conflict_do_update(
                index_elements=["idempotency_key"],
                set_={"idempotency_key": self.model.idempotency_key}
            )
            .values(**create_dto.model_dump())
            .returning(*returning_fields)
        )
        cursor = await self.session.execute(insert_query)
        data = dict(cursor.mappings().first())
        created = data.pop("is_created")
        return created, PaymentDTO(**data)


@dataclass
class OutboxRepository:
    model: ClassVar[Type[OutboxModel]] = OutboxModel

    session: AsyncSession

    async def create(self, create_dto: CreateOutboxDTO) -> OutboxDTO:
        returning_fields = get_returning_fields(self.model, OutboxDTO)

        insert_query = (
            pg_insert(self.model)
            .values(**create_dto.model_dump())
            .returning(*returning_fields)
        )
        cursor = await self.session.execute(insert_query)
        return OutboxDTO(**cursor.mappings().first())

