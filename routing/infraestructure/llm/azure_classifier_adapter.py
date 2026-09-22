import logging
import os
from openai import AsyncAzureOpenAI
from domain.models.message import WorkFlowTarget
from domain.ports.intent_classifier_port import IntentClassifierPort
from infraestructure.promps.promp_routing import SYSTEM_PROMPT
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

AZURE_MODEL = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-min")

class AzureClassifierAdapter(IntentClassifierPort):
    def __init__(self):
        self._deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
        self._client = AsyncAzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
        )

    async def classify(self, text: str) -> WorkFlowTarget:
        try:
            response = await self._client.chat.completions.create(
                model=self._deployment,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text}
                ],
                temperature=0.0,
                max_tokens=10
            )
            raw = response.choices[0].message.content.strip().upper()
            logger.info("Respuesta cruda de Azure OpenAI: '%s'", raw)
            if "RECLAMO" in raw: return WorkFlowTarget.TECHNICAL_CLAIM
            if "FACTURACION" in raw: return WorkFlowTarget.BILLING
            if "CONSULTA" in raw: return WorkFlowTarget.GENERAL_QUERY
            logger.warning("Intención no reconocida en Azure: '%s' -> asignando UNKNOWN", raw)
        except Exception as e:
            logger.error("Error al clasificar con Azure OpenAI: %s", e, exc_info=True)
        return WorkFlowTarget.UNKNOWN