from abc import ABC, abstractmethod


class StoragePort(ABC):
    @abstractmethod
    async def upload(self, file_bytes: bytes, filename: str, content_type: str = "image/jpeg") -> str:
        """
        Sube el archivo al almacenamiento (ej: MinIO/S3)
        y retorna la URL o path del archivo almacenado.
        """
        pass

