from dataclasses import dataclass

from application.services import ProcessPaymentService, NotifyService
from bootstrap.config.app import AppConfig
from bootstrap.config.pg import PgConfig
from bootstrap.config.rmq import RmqConfig
from bootstrap.db.factory import DbSessionFactory
from bootstrap.di_container import DIContainer
from bootstrap.interfaces import DbSessionFactoryInterface
from infrastructure.acquiring import AcquiringClient
from infrastructure.http import ConnectionPool, HttpSession
from infrastructure.repositories import PaymentRepository


@dataclass
class DIContainerFactory:
    app_config: AppConfig
    pg_config: PgConfig
    rmq_config: RmqConfig

    def build_di_container(self) -> DIContainer:
        container = DIContainer()

        # singletons
        container.register_instance(AppConfig, self.app_config)
        container.register_instance(PgConfig, self.pg_config)
        container.register_instance(RmqConfig, self.rmq_config)
        container.register_instance(
            DbSessionFactoryInterface, DbSessionFactory(pg_config=self.pg_config)
        )
        container.register_instance(ConnectionPool, ConnectionPool(size=10))

        # etc
        container.register(HttpSession)
        container.register(AcquiringClient)

        # services
        container.register(PaymentRepository)
        container.register(ProcessPaymentService)
        container.register(NotifyService)
        return container
