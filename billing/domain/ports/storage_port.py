from abc import ABC, abstractmethod


class StoragePort(ABC):
    @abstractmethod
    async def upload(self, file_bytes: bytes, filename: str, content_type:str = "image/jpg") -> str:
        """
        Sube el archivo al almacenamiento (ej: MinIO/S3)
        y retorna la URL o path del archivo almacenado.
        """
        """
        Upload the file to storage (e.g., MinIO/S3)
        and return the URL or path of the stored file.
        """
        pass
