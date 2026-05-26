from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        env_prefix="EVALOPS_",
        extra="ignore",
    )

    app_name: str = "EvalOps API"
    environment: str = "dev"
    api_prefix: str = "/api/v1"

    postgres_dsn: str = "postgresql+asyncpg://evalops:evalops@localhost:5432/evalops"
    alembic_dsn: str = "postgresql+psycopg2://evalops:evalops@localhost:5432/evalops"
    redis_url: str = "redis://localhost:6379/0"
    clickhouse_url: str = "http://localhost:8123"
    clickhouse_database: str = "evalops"
    worker_count: int = 2
    evaluator_timeout_seconds: int = 60


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
