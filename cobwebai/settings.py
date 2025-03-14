import enum
import os
from pathlib import Path
from tempfile import gettempdir

from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

TEMP_DIR = Path(gettempdir())


class LogLevel(str, enum.Enum):
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = "127.0.0.1"
    port: int = 8000
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    # Current environment
    environment: str = "dev"
    log_level: LogLevel = LogLevel.INFO
    users_secret: str = os.getenv("USERS_SECRET", "")
    openapi_key: str = os.getenv("OPENAI_API_KEY", "")
    ssl_certfile: str | None = None
    ssl_keyfile: str | None = None

    # Variables for the database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_pass: str = "postgres"
    db_base: str = "cobwebai"
    db_echo: bool = False

    chroma_host: str = "localhost"
    chroma_port: int = 35432

    redis_url: str = "redis://localhost:6379/0"

    s3_key_id: str | None = None
    s3_secret_key: str | None = None
    s3_region: str = "ru-central1"
    s3_endpoint_url: str = "https://storage.yandexcloud.net"

    s3_bucket_name: str = "cobweb-ai-data-i7qg8bs"

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="COBWEBAI_",
        env_file_encoding="utf-8",
    )


settings = Settings()
