from pydantic import Field
from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    debug: bool = Field(alias='DEBUG', default=False)
    secret_key: str = Field(alias='SECRET_KEY', default='wowsosecret')
    log_level: str = Field(alias='LOG_LEVEL', default='ERROR')
    api_key: str = Field(alias='API_KEY', default='noapikey')
    outbox_relay_interval_sec: int = Field(alias='OUTBOX_RELAY_INTERVAL_SEC', default=10)
    terminal_key: str = Field(alias='TERMINAL_KEY', default='someterminalkey')
