import logging
from google import  genai
from google.genai import types
from domain.ports.llm_provider_port import LlmProviderPort
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MODEL_GEMINI = os.getenv("MODEL_GEMINI", "gemini-3.5-flash-lite")

class GeminiLlmAdapter(LlmProviderPort):
    def __init__(self, model_id: str = MODEL_GEMINI):
        self._model_id = model_id
        self._fallback_models = ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.8-flash"]
        self._client = genai.Client(
            http_options=types.HttpOptions(
                timeout=12000,
                retry_options=types.HttpRetryOptions(attempts=1),
            )
        )

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        session_id: str | None = None,
        user_id: str | None = None,
        name: str = "billing-assistant"
    ) -> str:
        models_to_try = [self._model_id] + [m for m in self._fallback_models if m != self._model_id]
        last_error = None

        for model_name in models_to_try:
            try:
                response = await self._client.aio.models.generate_content(
                    model=model_name,
                    contents= user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.0,
                        response_mime_type="application/json"
                    ),
                )
                return response.text or "{}"
            except Exception as e:
                last_error = e
                logger.warning("Modelo '%s' con alta demanda (%s), probando fallback...", model_name, e)

        logger.error("Error generating response with Gemini: %s", last_error, exc_info=True)
        raise last_error