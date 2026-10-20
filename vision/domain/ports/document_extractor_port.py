from abc import ABC, abstractmethod
from domain.models.extracted_document_model import ExtractedDocumentModel


class DocumentExtractorPort(ABC):
    @abstractmethod
    async def extract_from_image(self, image_bytes: bytes) -> ExtractedDocumentModel:
        """
        Analiza la imagen con visión/OCR, detecta qué tipo de documento es
        (Factura, Comprobante o Reclamo Técnico) y extrae sus datos estructurados.
        """
        pass

