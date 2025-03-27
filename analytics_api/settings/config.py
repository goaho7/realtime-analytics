from pydantic_settings import BaseSettings
from typing import Optional, Dict


class Settings(BaseSettings):
    POSTGRES_DB: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_HOST_NAME: Optional[str] = None
    POSTGRES_PORT: Optional[int] = None

    ACCESS_KEY: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    ENDPOINT_URL: Optional[str] = None
    BUCKET_NAME: Optional[str] = None

    def async_postgres_connect(self) -> str:
        """Формирует строку подключения к PostgreSQL с использованием asyncpg."""
        user = self.POSTGRES_USER
        password = self.POSTGRES_PASSWORD
        host = self.POSTGRES_HOST_NAME
        port = self.POSTGRES_PORT
        db = self.POSTGRES_DB

        if any(v is None for v in [user, password, host, port, db]):
            raise ValueError(
                "Недостаточно данных для формирования строки подключения к PostgreSQL"
            )

        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

    def get_s3_conf(self) -> Dict[str, Optional[str]]:
        access_key_id = self.ACCESS_KEY
        access_key = self.SECRET_KEY
        endpoint_url = self.ENDPOINT_URL

        if any(v is None for v in [access_key_id, access_key, endpoint_url]):
            raise ValueError("Недостаточно данных для подключения к S3")

        return {
            "aws_access_key_id": access_key_id,
            "aws_secret_access_key": access_key,
            "endpoint_url": endpoint_url,
        }

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
