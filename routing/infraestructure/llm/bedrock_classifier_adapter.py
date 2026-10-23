import logging
import os
from dotenv import load_dotenv
try:
    from langfuse.openai import AsyncOpenAI
except ImportError:
    from openai import AsyncOpenAI
from domain.models.message import WorkFlowTarget
from domain.ports.intent_classifier_port import IntentClassifierPort
from infraestructure.promps.promp_routing import SYSTEM_PROMPT

load_dotenv()

logger = logging.getLogger(__name__)


class BedrockClassifierAdapter(IntentClassifierPort):

    def __init__(self, model_id: str | None = None):
        self._model = model_id or os.getenv("OPENAI_MODEL", "openai.gpt-oss-120b")
        self._client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://bedrock-mantle.us-east-2.api.aws/v1")
        )

    async def classify(self, text: str, session_id: str | None = None, user_id: str | None = None) -> WorkFlowTarget:
        try:
            extra_kwargs = {"name": "routing-classifier"}
            if session_id:
                extra_kwargs["session_id"] = session_id
            if user_id:
                extra_kwargs["user_id"] = user_id

            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text}
                ],
                temperature=0.0,
                max_tokens=300,
                **extra_kwargs
            )
            choice = response.choices[0]
            raw = (choice.message.content or "").strip().upper()

            # Si el modelo consumió tokens en reasoning, extraemos la categoría también de ahí
            if not raw and getattr(choice.message, "reasoning", None):
                raw = choice.message.reasoning.strip().upper()

            logger.info("Respuesta de Bedrock Mantle: '%s'", raw)

            if "RECLAMO" in raw:
                return WorkFlowTarget.TECHNICAL_CLAIM
            elif "FACTURACION" in raw:
                return WorkFlowTarget.BILLING
            elif "CONSULTA" in raw:
                return WorkFlowTarget.GENERAL_QUERY

            logger.warning("Intención no reconocida: '%s' -> asignando UNKNOWN", raw)
            return WorkFlowTarget.UNKNOWN
        except Exception as e:
            logger.error("Error clasificando con Bedrock Mantle: %s", e, exc_info=True)
            return WorkFlowTarget.UNKNOWN
