import logging
import os
from domain.ports.llm_provider_port import LlmProviderPort
from infrastructure.llm.providers.bedrock_llm_adapter import BedrockLlmAdapter
from infrastructure.llm.providers.gemini_llm_adapter import GeminiLlmAdapter

logger = logging.getLogger(__name__)


class LLMFactory:

    @staticmethod
    def get_llm_provider() -> LlmProviderPort:
        provider = os.getenv("LLM_PROVIDER", "bedrock").lower()
        logger.info("Inicializando LlmProviderPort para: '%s'", provider)

        if provider in ("aws", "bedrock", "openai"):
            return BedrockLlmAdapter()
        elif provider in ("google", "gemini"):
            return GeminiLlmAdapter()
        else:
            raise ValueError(f"Proveedor LLM desconocido: {provider}. Opciones válidas: bedrock, gemini")
