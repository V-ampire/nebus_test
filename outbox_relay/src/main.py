import asyncio
import logging

from faststream.rabbit import RabbitBroker

from bootstrap.config.app import AppConfig
from bootstrap.config.pg import PgConfig
from bootstrap.config.rmq import RmqConfig
from bootstrap.db.factory import DbSessionFactory
from bootstrap.utils import str_exception
from relay import RelayService
from repository import OutboxRepository


logger = logging.getLogger(__name__)


async def main():
    pg_config = PgConfig()
    app_config = AppConfig()
    rmq_config = RmqConfig()
    session_factory = DbSessionFactory(pg_config=pg_config)
    async with RabbitBroker(rmq_config.dsn) as broker:
        logger.info("Outbox relay started")
        while True:
            try:
                async_session = session_factory.get_session()
                async with async_session() as session:
                    relay_service = RelayService(
                        rmq_config=rmq_config,
                        outbox_repository=OutboxRepository(session=session),
                        broker=broker
                    )
                    new_events = await relay_service.get_new_events()
                    for event in new_events:
                        await relay_service.enqueue_event(event)
                        await relay_service.set_event_sent(event)
                        logger.info(f"Outbox relay sent {event.event_id} event")
                    await session.commit()
                    logger.info(f"Outbox relay processed {len(new_events)} events")
            except Exception as exc:
                logger.error(str_exception(exc))
            await asyncio.sleep(app_config.outbox_relay_interval_sec)


if __name__ == "__main__":
    asyncio.run(main())


