import os
import logging
from typing import List, Dict, Optional
from domain.port.consulting_llm_port import ConsultingLlmPort
from domain.models.knowledge_chunk_model import KnowledgeChunkModel
from domain.models.consulting_result_model import ConsultingResultModel
from domain.promps.consulting_system_prompt import (
    CONSULTING_SYSTEM_PROMPT,
    BUILD_CONSULTING_USER_PROMPT,
)

try:
    from langfuse.openai import AsyncOpenAI
except ImportError:
    from openai import AsyncOpenAI
try:
    from aws_bedrock_token_generator import provide_token
except ImportError:
    provide_token = None

logger = logging.getLogger(__name__)

class BedrockConsultingLlmAdapter(ConsultingLlmPort):
    def __init__(self, model_id: Optional[str]= None):
        self._model = model_id or os.getenv("OPENAI_MODEL", "openai.gpt-oss-120b")
        self._base_url = os.getenv("OPENAI_BASE_URL", "https://bedrock-mantle.us-east-2.api.aws/v1")

        token = os.getenv("OPENAI_API_KEY")
        if not token and provide_token:
            token = provide_token(region="us-east-2")
        self._client = AsyncOpenAI(
            api_key=token,
            base_url=self._base_url,
        )

    async def generate_response(self, query, context_chunks, chat_history):
        try:
            user_prompt = BUILD_CONSULTING_USER_PROMPT(query=query, context_chunks=context_chunks)
            messages = [{"role": "system", "content": CONSULTING_SYSTEM_PROMPT}]

            if chat_history:
                for msg in chat_history[:-1]:
                    messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": user_prompt})

            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=0.1,
                max_tokens=1500,
            )
            choice = response.choices[0]
            answer = choice.message.content or getattr(choice.message, "reasoning", "") or ""
            sources = list({c.source for c in context_chunks})
            return ConsultingResultModel(response_text=answer, sources=sources)

        except Exception as e:
            logger.error("Error llamando a Bedrock Mantle: %s. Intentando fallback con Gemini...", e)
            try:
                from google import genai
                from google.genai import types
                client = genai.Client()
                gemini_resp = await client.aio.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=CONSULTING_SYSTEM_PROMPT,
                        temperature=0.1,
                        max_output_tokens=1500,
                    ),
                )
                answer = gemini_resp.text or ""
                sources = list({c.source for c in context_chunks})
                return ConsultingResultModel(response_text=answer, sources=sources)
            except Exception as fb_err:
                logger.error("Error en fallback Gemini: %s", fb_err)
                return ConsultingResultModel(
                    response_text="Disculpá, tuvimos un inconveniente técnico momentáneo al consultar la información. Por favor intentá nuevamente en unos instantes o comunicate con el 0800-777-EDET (3338).",
                    sources=[],
                )

