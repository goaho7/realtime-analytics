from contextlib import asynccontextmanager

from aiobotocore.session import get_session


class S3Client:

    def __init__(self, s3_config: dict, bucket_name: str):
        self.s3_config = s3_config
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.s3_config) as client:
            yield client

    async def upload_file(self, file, file_name):
        async with self.get_client() as client:
            await client.put_object(Bucket=self.bucket_name, Key=file_name, Body=file)
