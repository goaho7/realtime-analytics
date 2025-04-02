from fastapi import Request

from src.service.s3_service import S3Service
from src.service.s3_client import S3Client


def get_s3_client(request: Request) -> S3Client:
    return request.app.state.s3_client


def get_s3_service(request: Request) -> S3Service:
    return request.app.state.s3_service
