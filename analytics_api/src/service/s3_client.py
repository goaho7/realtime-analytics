import logging

from contextlib import asynccontextmanager
from typing import BinaryIO, Union
from mimetypes import guess_type

from aiobotocore.session import get_session

logger = logging.getLogger(__name__)


class S3Client:

    def __init__(self, s3_config: dict, bucket_name: str):
        required_keys = {"aws_access_key_id", "aws_secret_access_key", "endpoint_url"}
        missing_keys = required_keys - set(s3_config.keys())
        if missing_keys:
            raise ValueError(
                f"Missing required S3 config keys: {', '.join(missing_keys)}"
            )
        invalid_keys = {
            k
            for k, v in s3_config.items()
            if v is None or (isinstance(v, str) and not v.strip())
        }
        if invalid_keys:
            raise ValueError(
                f"Invalid (None or empty) S3 config values for keys: {', '.join(invalid_keys)}"
            )

        self.s3_config = s3_config
        self.bucket_name = bucket_name

    @asynccontextmanager
    async def get_client(self):
        session = get_session()
        async with session.create_client("s3", **self.s3_config) as client:
            yield client

    async def upload_file(self, file: Union[bytes, BinaryIO], file_name: str) -> None:
        """Загружает файл в S3"""
        content_type, _ = guess_type(file_name)
        content_type = content_type or "application/octet-stream"

        async with self.get_client() as client:
            try:
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=file_name,
                    Body=file,
                    ContentType=content_type,
                )
                logger.info(f"Successfully uploaded {file_name} to {self.bucket_name}")
            except Exception as e:
                logger.error(f"Failed to upload {file_name} to S3: {str(e)}")
                raise

    async def delete_file(self, file_name: str) -> None:
        """Удаляет файл из S3"""
        async with self.get_client() as client:
            try:
                await client.delete_object(Bucket=self.bucket_name, Key=file_name)
                logger.info(f"Successfully deleted {file_name} from {self.bucket_name}")
            except Exception as e:
                logger.error(f"Failed to delete {file_name} from S3: {str(e)}")
                raise
