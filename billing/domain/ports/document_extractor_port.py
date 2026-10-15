from abc import ABC, abstractmethod
from domain.models.extracted_document_model import  ExtractedDocumentModel

class DocumentExtractorPort(ABC):
    @abstractmethod
    async def extract_from_image(self, image_bytes: bytes )-> ExtractedDocumentModel:
        """
        Analiza la imagen con visión/OCR, detecta qué tipo de documento es 
        (Factura o Comprobante) y extrae sus datos estructurados.
        """
        """
        Analyze the image using OCR/vision, detect what type of document it is (Invoice or Receipt)
        , and extract its structured data.
        """
        pass
