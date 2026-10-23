import logging
import os 
from domain.ports.intent_classifier_port import IntentClassifierPort
from infraestructure.llm.bedrock_classifier_adapter import BedrockClassifierAdapter
from infraestructure.llm.gemini_classifier_adapter import GoogleVertexClassifierAdapter

logger = logging.getLogger(__name__)


class LLMFactory:
    @staticmethod
    def get_classifier() -> IntentClassifierPort:
        provider = os.getenv("LLM_PROVIDER", "bedrock").lower()
        logger.info("Inicializando adaptador LLM para el proveedor: '%s'", provider)

        if provider in ("aws", "bedrock", "openai"):
            return BedrockClassifierAdapter()
        elif provider in ("google", "gemini"):
            return GoogleVertexClassifierAdapter()
        else:
            raise ValueError(f"Proveedor LLM desconocido: {provider}. Opciones válidas: bedrock, gemini")
