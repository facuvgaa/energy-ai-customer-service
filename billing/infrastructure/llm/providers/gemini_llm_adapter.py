import logging
from google import  genai
from google.genai import types
from domain.ports.llm_provider_port import LlmProviderPort
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MODEL_GEMINI = os.getenv("MODEL_GEMINI", "gemini-3.8-flash")

class GeminiLlmAdapter(LlmProviderPort):
    def __init__(self, model_id: str = MODEL_GEMINI):
        self._model_id = model_id
        self._client = genai.Client()

    async def generate(self, system_prompt, user_prompt)-> str:
        try: 
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents= user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.0,
                    response_mime_type="application/json"
                ),
            )
            return response.text or "{}"
        except Exception as e:
            logger.error("Error generating response with Gemini", e, exc_info=True)
            raise