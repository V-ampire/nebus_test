from contextlib import asynccontextmanager

from faststream import FastStream, ContextRepo
from faststream.rabbit import RabbitBroker, RabbitQueue, RabbitExchange, ExchangeType

from bootstrap.config.app import AppConfig
from bootstrap.config.pg import PgConfig
from bootstrap.config.rmq import RmqConfig
from infrastructure.di import DIContainerFactory
from infrastructure.http import ConnectionPool
from presentation import handlers


def init_broker(rmq_config: RmqConfig) -> RabbitBroker:
    broker = RabbitBroker(rmq_config.dsn)

    payments_queue = RabbitQueue(
        rmq_config.processing_queue,
        durable=True,
        arguments={
            "x-dead-letter-exchange": rmq_config.processing_dlq_exchange,
            "x-dead-letter-routing-key": rmq_config.processing_dlq,
            "x-delivery-count": None,
        },
    )
    payments_exchange = RabbitExchange(
        "payments",
        type=ExchangeType.DIRECT,
        durable=True,
    )
    dlx = RabbitExchange(
        rmq_config.processing_dlq_exchange,
        type=ExchangeType.DIRECT,
        durable=True,
    )
    dlq = RabbitQueue(
        rmq_config.processing_dlq,
        durable=True,
        routing_key=rmq_config.processing_dlq,
    )

    messages_sub = broker.subscriber(payments_queue, payments_exchange)
    messages_sub(handlers.process_payment)

    messages_sub = broker.subscriber(dlq, dlx)
    messages_sub(handlers.process_dlq)

    return broker


@asynccontextmanager
async def lifespan(context: ContextRepo):
    app_config = AppConfig()
    pg_config = PgConfig()
    rmq_config = RmqConfig()

    di_container_factory = DIContainerFactory(
        app_config=app_config,
        pg_config=pg_config,
        rmq_config=rmq_config,
    )
    di_container = di_container_factory.build_di_container()
    context.set_global('di_container', di_container)
    pool = di_container.resolve(ConnectionPool)
    try:
        yield
    finally:
        await pool.close()

def init_app() -> FastStream:
    rmq_config = RmqConfig()
    broker = init_broker(rmq_config)
    return FastStream(broker, lifespan=lifespan)
