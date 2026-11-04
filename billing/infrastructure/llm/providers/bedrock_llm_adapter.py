import logging
import os
from dotenv import load_dotenv
try:
    from langfuse.openai import AsyncOpenAI
except ImportError:
    from openai import AsyncOpenAI
from domain.ports.llm_provider_port import LlmProviderPort

load_dotenv()

logger = logging.getLogger(__name__)


class BedrockLlmAdapter(LlmProviderPort):

    def __init__(self, model_id: str | None = None):
        self._model = model_id or os.getenv("OPENAI_MODEL", "openai.gpt-oss-120b")
        self._client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://bedrock-mantle.us-east-2.api.aws/v1")
        )

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        session_id: str | None = None,
        user_id: str | None = None,
        name: str = "billing-assistant"
    ) -> str:
        try:
            extra_kwargs = {"name": name}
            if session_id:
                extra_kwargs["session_id"] = session_id
            if user_id:
                extra_kwargs["user_id"] = user_id

            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                max_tokens=2000,
                **extra_kwargs
            )
            choice = response.choices[0]
            return choice.message.content or getattr(choice.message, "reasoning", "") or "{}"
        except Exception as e:
            logger.error("Error generating response with Bedrock Mantle: %s. Probando fallback con Gemini...", e)
            try:
                from infrastructure.llm.providers.gemini_llm_adapter import GeminiLlmAdapter
                gemini = GeminiLlmAdapter()
                return await gemini.generate(system_prompt, user_prompt, session_id, user_id, name)
            except Exception as fb_err:
                logger.error("Error en fallback Gemini para billing: %s", fb_err)
                raise e

