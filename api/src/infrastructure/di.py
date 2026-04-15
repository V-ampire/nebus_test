from dataclasses import dataclass

from application.services import PaymentService
from bootstrap.config.app import AppConfig
from bootstrap.config.pg import PgConfig
from bootstrap.config.rmq import RmqConfig
from bootstrap.interfaces import DbSessionFactoryInterface
from bootstrap.db.factory import DbSessionFactory
from bootstrap.di_container import DIContainer
from infrastructure.repositories import PaymentRepository, OutboxRepository


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

        container.register(PaymentRepository)
        container.register(OutboxRepository)
        container.register(PaymentService)
        return container
