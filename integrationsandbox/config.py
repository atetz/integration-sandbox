import secrets
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


@lru_cache
def get_settings():
    return Settings()


class Settings(BaseSettings):
    default_user: str = "sandy"
    default_password: str = "sandbox"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 15
    jwt_secret_key: str = secrets.token_hex(32)
    webhook_api_key: str = secrets.token_hex(32)
    max_bulk_size: int = 1000
    float_precision: int = 2
    database_path: str = "integrationsandbox/infrastructure/db.sqlite3"
    log_file_path: str = "fastapi.log"
    log_file_maxbytes: int = 10485760
    log_level: str = "INFO"
    cors_origins: list[str] = ["*"]
    cors_credentials: bool = True
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def log_config(self):
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": self.log_level,
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": self.log_level,
                    "formatter": "default",
                    "filename": self.log_file_path,
                    "maxBytes": self.log_file_maxbytes,
                    "backupCount": 5,
                },
            },
            "loggers": {
                "integrationsandbox": {
                    "handlers": ["console", "rotating_file"],
                    "level": self.log_level,
                    "propagate": False,
                },
                "uvicorn": {
                    "handlers": ["console", "rotating_file"],
                    "level": self.log_level,
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["console", "rotating_file"],
                    "level": self.log_level,
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["console", "rotating_file"],
                    "level": self.log_level,
                    "propagate": False,
                },
            },
        }


tags_metadata = [
    {
        "name": "Broker",
        "description": "Interact with the Broker sandbox.",
    },
    {
        "name": "TMS",
        "description": "Interact with the TMS sandbox.",
    },
    {
        "name": "Trigger",
        "description": "Send TMS shipments or Broker events to a webhook.",
    },
    {
        "name": "System",
        "description": "Operations with sys health and users. The **login** logic is also here.",
    },
]
