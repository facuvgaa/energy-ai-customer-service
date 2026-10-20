import logging
import os
from domain.ports.document_extractor_port import DocumentExtractorPort
from infrastructure.llm.extractor.gemini_document_extractor_adapter import GeminiDocumentExtractorAdapter

logger = logging.getLogger(__name__)


class VisionLLMFactory:
    @staticmethod
    def get_document_extractor() -> DocumentExtractorPort:
        provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        logger.info("Inicializando DocumentExtractorPort en Vision para: '%s'", provider)

        if provider in ("google", "gemini"):
            return GeminiDocumentExtractorAdapter()
        else:
            raise ValueError(f"Extractor desconocido para proveedor: {provider}")

