import logging
import os
from domain.ports.llm_provider_port import LlmProviderPort
from domain.ports.document_extractor_port import DocumentExtractorPort
from infrastructure.llm.providers.gemini_llm_adapter import GeminiLlmAdapter
from infrastructure.llm.extractor.gemini_document_extractor_adapter import GeminiDocumentExtractorAdapter

logger = logging.getLogger(__name__)


class LLMFactory:

    @staticmethod
    def get_llm_provider() -> LlmProviderPort:
        provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        logger.info("Inicializando LlmProviderPort para: '%s'", provider)

        if provider in ("google", "gemini"):
            return GeminiLlmAdapter()
        else:
            raise ValueError(f"Proveedor LLM desconocido: {provider}")

    @staticmethod
    def get_document_extractor() -> DocumentExtractorPort:
        provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        logger.info("Inicializando DocumentExtractorPort para: '%s'", provider)

        if provider in ("google", "gemini"):
            return GeminiDocumentExtractorAdapter()
        else:
            raise ValueError(f"Extractor desconocido para proveedor: {provider}")