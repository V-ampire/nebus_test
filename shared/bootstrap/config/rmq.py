from pydantic import Field
from pydantic_settings import BaseSettings


class RmqConfig(BaseSettings):
    user: str = Field(alias='RABBITMQ_DEFAULT_USER')
    password: str = Field(alias='RABBITMQ_DEFAULT_PASS')
    host: str = Field(alias='RABBITMQ_HOST')
    port: int = Field(alias='RABBITMQ_PORT')
    processing_queue: str = Field(alias='PROCESSING_QUEUE', default="payments.new")
    processing_queue_exchange: str = Field(alias='PROCESSING_QUEUE_EXCHANGE', default="payments")
    processing_dlq_exchange: str = Field(alias='PROCESSING_DLQ_EXCHANGE', default="payments.dlx")
    processing_dlq: str = Field(alias='PROCESSING_DLQ', default="payments.dlq")

    @property
    def dsn(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/"
