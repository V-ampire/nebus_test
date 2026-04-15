from pydantic import Field
from pydantic_settings import BaseSettings


class PgConfig(BaseSettings):
    user: str = Field(alias='POSTGRES_USER')
    password: str = Field(alias='POSTGRES_PASSWORD')
    host: str = Field(alias='POSTGRES_HOST')
    port: int = Field(alias='POSTGRES_PORT')
    db: str = Field(alias='POSTGRES_DB')
    echo: bool = Field(alias='POSTGRES_ECHO')

    @property
    def async_dsn(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    @property
    def sync_dsn(self) -> str:
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"
