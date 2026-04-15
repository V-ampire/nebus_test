from dataclasses import dataclass

from pydantic import UUID4

from bootstrap.config.app import AppConfig
from bootstrap.types import OutboxStatus
from core.dto import CreatePaymentDTO, PaymentDTO, OutboxDTO, CreateOutboxDTO
from infrastructure.repositories import PaymentRepository, OutboxRepository


@dataclass
class PaymentService:
    app_config: AppConfig
    payment_repository: PaymentRepository
    outbox_repository: OutboxRepository

    async def create_idempotency_payment(self, create_data: CreatePaymentDTO) -> PaymentDTO:
        created, payment = await self.payment_repository.create_with_idempotency(create_data)
        if created:
            await self.outbox_repository.create(CreateOutboxDTO(
                status=OutboxStatus.NEW,
                payload=payment.model_dump(mode="json")
            ))
        return payment

    async def get_payment_by_id(self, payment_id: UUID4) -> PaymentDTO:
        return await self.payment_repository.fetch(id=payment_id)




