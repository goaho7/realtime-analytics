from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    POSTGRES_DB: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_HOST_NAME: Optional[str] = None
    POSTGRES_PORT: Optional[int] = None

    ACCESS_KEY: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    ENDPOINT_URL: Optional[str] = None

    def async_postgres_connect(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST_NAME}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    def get_s3_conf(self) -> dict:
        return {
            "aws_access_key_id": self.ACCESS_KEY,
            "aws_secret_access_key": self.SECRET_KEY,
            "endpoint_url": self.ENDPOINT_URL,
        }

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
