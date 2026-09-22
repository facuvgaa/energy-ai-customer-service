import logging
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from domain.models.message import WorkFlowTarget
from domain.ports.intent_classifier_port import IntentClassifierPort
from infraestructure.promps.promp_routing import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

load_dotenv()

MODEL_GEMINI = os.getenv("MODEL_GEMINI", "gemini-2.5-flash")


class GoogleVertexClassifierAdapter(IntentClassifierPort):

    def __init__(self, model_id: str = MODEL_GEMINI):
        self._model = model_id
        self._client = genai.Client()

    async def classify(self, text: str) -> WorkFlowTarget:
        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=text,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.0,
                    max_output_tokens=150,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                ),
            )

            raw_text = (response.text or "").strip().upper()
            logger.debug("Respuesta del modelo: '%s'", raw_text)

            clean_text = raw_text.replace('"', '').replace("'", '').replace("`", "").strip().upper()

            logger.info("Respuesta cruda: '%s' -> limpia: '%s'", raw_text, clean_text)

            if "RECLAMO" in raw_text:
                return WorkFlowTarget.TECHNICAL_CLAIM
            elif "FACTURACION" in raw_text:
                return WorkFlowTarget.BILLING
            elif "CONSULTA" in raw_text:
                return WorkFlowTarget.GENERAL_QUERY

            logger.warning("Intención no reconocida: '%s' -> asignando UNKNOWN", raw_text)
            return WorkFlowTarget.UNKNOWN

        except Exception as e:
            logger.error("Error en clasificación Gemini: %s", e, exc_info=True)
            return WorkFlowTarget.UNKNOWN