import logging
from dataclasses import dataclass

from faststream.rabbit import RabbitBroker

from bootstrap.config.app import AppConfig
from bootstrap.config.rmq import RmqConfig
from bootstrap.retry import retry_factory
from bootstrap.types import OutboxStatus
from dto import OutboxDTO
from repository import OutboxRepository


logger = logging.getLogger(__name__)


@dataclass
class RelayService:
    rmq_config: RmqConfig
    outbox_repository: OutboxRepository
    broker: RabbitBroker

    async def get_new_events(self) -> list[OutboxDTO]:
        return await self.outbox_repository.fetch_many(select_for_update=True, status=OutboxStatus.NEW)

    async def set_event_sent(self, outbox: OutboxDTO):
        return await self.outbox_repository.update(outbox.event_id, dict(status=OutboxStatus.SENT))

    @retry_factory(logger)
    async def enqueue_event(self, outbox: OutboxDTO) -> None:
        await self.broker.publish(outbox.payload['id'], self.rmq_config.processing_queue)
