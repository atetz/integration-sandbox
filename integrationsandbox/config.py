from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


@lru_cache
def get_settings():
    return Settings()


class Settings(BaseSettings):
    max_bulk_size: int = 1000
    float_precision: int = 2
    database_path: str = "integrationsandbox/infrastructure/db.sqlite3"
    log_level: str = "INFO"
    cors_origins: list[str] = ["*"]
    cors_credentials: bool = True
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env")
