import asyncio
import io
import logging
import os
from minio import Minio
from domain.ports.storage_port import StoragePort

logger = logging.getLogger(__name__)


class MinioStorageAdapter(StoragePort):
    def __init__(
        self,
        endpoint: str = os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        access_key: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key: str = os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        bucket_name: str = os.getenv("MINIO_BUCKET", "billing-documents"),
        secure: bool = False,
    ):
        self._endpoint = endpoint
        self._bucket = bucket_name
        self._client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

    def _sync_upload(self, file_bytes: bytes, filename: str, content_type: str) -> str:
        if not self._client.bucket_exists(self._bucket):
            logger.info("Creando bucket '%s' en MinIO", self._bucket)
            self._client.make_bucket(self._bucket)

        file_stream = io.BytesIO(file_bytes)

        self._client.put_object(
            bucket_name=self._bucket,
            object_name=filename,
            data=file_stream,
            length=len(file_bytes),
            content_type=content_type,
        )

        return f"http://{self._endpoint}/{self._bucket}/{filename}"

    async def upload(
        self, file_bytes: bytes, filename: str, content_type: str = "image/jpeg"
    ) -> str:
        try:
            url = await asyncio.to_thread(
                self._sync_upload, file_bytes, filename, content_type
            )
            logger.info("Imagen guardada exitosamente en MinIO: %s", url)
            return url
        except Exception as e:
            logger.error("Error subiendo archivo '%s' a MinIO: %s", filename, e, exc_info=True)
            raise

