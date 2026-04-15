import logging
from dataclasses import dataclass
from datetime import datetime

from pydantic import UUID4

from bootstrap.config.app import AppConfig
from bootstrap.retry import retry_factory
from bootstrap.types import PaymentStatus
from core.dto import PaymentDTO, WebhookDTO
from infrastructure.acquiring import AcquiringClient, AcquiringRequest, AcquiringResponse
from infrastructure.http import HttpSession
from infrastructure.repositories import PaymentRepository


logger = logging.getLogger(__name__)


@dataclass
class NotifyService:
    http: HttpSession

    @retry_factory(logger)
    async def send_webhook(self, webhook_data: WebhookDTO):
        return await self.http.post(webhook_data.url, webhook_data.model_dump(mode='json', exclude={'url'}))


@dataclass
class ProcessPaymentService:
    app_config: AppConfig
    payment_repository: PaymentRepository
    client: AcquiringClient

    @retry_factory(logger)
    async def acquire_payment(self, payment: PaymentDTO) -> AcquiringResponse:
        payload = AcquiringRequest(
            terminal_key=self.app_config.terminal_key,
            amount=payment.amount,
            order_id=str(payment.id),
        )
        return await self.client.init_payment(payload)

    async def process_payment(self, payment_id: UUID4) -> WebhookDTO | None:
        payment = await self.payment_repository.fetch(select_for_update=True, id=payment_id)
        if payment.status != PaymentStatus.PENDING:
            return

        response = await self.acquire_payment(payment)

        update_data = dict(
            status=PaymentStatus.SUCCEEDED if response.success else PaymentStatus.FAILED,
            acquiring_data = response.model_dump(mode='json'),
            processed_at=datetime.now(),
        )
        updated = await self.payment_repository.update(payment_id, update_data)

        return WebhookDTO(
            url=payment.webhook_url,
            payment_id=updated.id,
            amount=updated.amount,
            staus=updated.status,
            acquiring_message=response.message
        )