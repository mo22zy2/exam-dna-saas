import logging
import os
import uuid
from abc import ABC, abstractmethod
from datetime import timedelta

import aiofiles
import boto3
import magic
from botocore.config import Config as BotoConfig
from pypdf import PdfReader

from app.config import settings

logger = logging.getLogger(__name__)


class StorageBackend(ABC):

    @abstractmethod
    async def save(self, file_key: str, content: bytes) -> str:
        ...

    @abstractmethod
    async def read(self, file_key: str) -> bytes:
        ...

    @abstractmethod
    async def delete(self, file_key: str) -> None:
        ...


class LocalStorageBackend(StorageBackend):

    def __init__(self, base_path: str = settings.upload_storage_path) -> None:
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    async def save(self, file_key: str, content: bytes) -> str:
        full_path = os.path.join(self.base_path, file_key)
        dir_path = os.path.dirname(full_path)
        os.makedirs(dir_path, exist_ok=True)
        async with aiofiles.open(full_path, "wb") as f:
            await f.write(content)
        return full_path

    async def read(self, file_key: str) -> bytes:
        full_path = os.path.join(self.base_path, file_key)
        async with aiofiles.open(full_path, "rb") as f:
            from typing import cast
            return cast(bytes, await f.read())

    async def delete(self, file_key: str) -> None:
        full_path = os.path.join(self.base_path, file_key)
        if os.path.exists(full_path):
            os.remove(full_path)


class R2StorageBackend(StorageBackend):

    def __init__(self) -> None:
        self.bucket = settings.r2_bucket_name
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.r2_endpoint_url,
            region_name=settings.r2_region,
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            config=BotoConfig(signature_version="s3v4"),
        )

    async def save(self, file_key: str, content: bytes) -> str:
        self.client.put_object(Bucket=self.bucket, Key=file_key, Body=content)
        logger.info("Saved file to R2: bucket=%s key=%s size=%d", self.bucket, file_key, len(content))
        return file_key

    async def read(self, file_key: str) -> bytes:
        resp = self.client.get_object(Bucket=self.bucket, Key=file_key)
        return resp["Body"].read()

    async def delete(self, file_key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=file_key)
        logger.info("Deleted file from R2: bucket=%s key=%s", self.bucket, file_key)


def _get_storage() -> StorageBackend:
    if settings.r2_endpoint_url and settings.r2_access_key_id:
        logger.info("Using R2StorageBackend")
        return R2StorageBackend()
    logger.info("Using LocalStorageBackend")
    return LocalStorageBackend()


storage = _get_storage()


def generate_storage_key(user_id: uuid.UUID, file_id: uuid.UUID) -> str:
    return f"{user_id}/{file_id}.pdf"


def generate_client_upload_id() -> uuid.UUID:
    return uuid.uuid4()


def generate_presigned_upload_url(storage_key: str, expires: int = 900) -> str:
    if isinstance(storage, R2StorageBackend):
        return storage.client.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": storage.bucket, "Key": storage_key},
            ExpiresIn=expires,
            HttpMethod="PUT",
        )
    return f"{settings.app_url}/upload/storage/{storage_key}"


PDF_MAGIC_BYTES = b"%PDF"


def is_valid_pdf(content: bytes) -> bool:
    if not content.startswith(PDF_MAGIC_BYTES):
        return False
    try:
        PdfReader.__module__
    except ImportError:
        pass
    return True


def validate_pdf_content(content: bytes) -> tuple[bool, str]:
    try:
        mime = magic.from_buffer(content, mime=True)
        if mime != "application/pdf":
            return False, f"Unexpected MIME type: {mime}"
        return True, ""
    except Exception as e:
        return False, f"Content validation failed: {str(e)}"
