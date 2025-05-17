from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    SENTRY_DSN: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
