import logging
import os 
from domain.ports.intent_classifier_port import IntentClassifierPort
from infraestructure.llm.azure_classifier_adapter import AzureClassifierAdapter
from infraestructure.llm.bedrock_classifier_adapter import BedrockClassifierAdapter
from infraestructure.llm.gemini_classifier_adapter import GoogleVertexClassifierAdapter

logger = logging.getLogger(__name__)

class LLMFactory():
    @staticmethod
    def get_classifier() -> IntentClassifierPort:
        provider = os.getenv("LLM_PROVIDER", "aws").lower()
        logger.info("Inicializando adaptador LLM para el proveedor: '%s'", provider)

        if provider == "aws" or provider == "bedrock":
           return BedrockClassifierAdapter()
        if provider == "google" or provider == "gemini":
            return GoogleVertexClassifierAdapter()
        if provider == "azure" or provider == "microsoft":
            return AzureClassifierAdapter()
        else:
            raise ValueError(f"Proveedor LLM desconocido: {provider}. Opciones válidas: aws, google, azure")