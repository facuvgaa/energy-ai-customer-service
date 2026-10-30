import json
import logging
import os
from typing import Optional, List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[4] / "claims" / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv()

try:
    from langfuse.openai import AsyncOpenAI
except ImportError:
    from openai import AsyncOpenAI

from domain.ports.llm_provider_port import LlmProviderPort
from domain.models.llm_decision_model import LlmDecision, LlmToolCall

load_dotenv()

logger = logging.getLogger(__name__)


class BedrockLlmAdapter(LlmProviderPort):
    def __init__(self, model_id: Optional[str] = None):
        self._model = model_id or os.getenv("OPENAI_MODEL", os.getenv("BEDROCK_MODEL", "openai.gpt-oss-120b"))
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("AWS_BEARER_TOKEN_BEDROCK")
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=os.getenv("OPENAI_BASE_URL", "https://bedrock-mantle.us-east-2.api.aws/v1"),
        )

    def _convert_mcp_tools_to_openai(self, tools:List[Dict[str,Any]])-> List[Dict[str,Any]]:

        openai_tools = []
        for t in tools:
            openai_tools.append({
                "type":"function",
                "function":{
                    "name": t.get("name"),
                    "description": t.get("description", ""),
                    "parameters": t.get("input_schema", {"type": "object", "properties": {}}),
                }
            })
    async def generate_decision(self, system_prompt, user_prompt, tools = None, session_id = None, user_id = None, name = "claims-assistant")-> LlmDecision:
        
        try:

            extra_kwargs: Dict[str, Any] = {"name": name}
            if session_id:
                extra_kwargs["session_id"] = session_id
            if user_id:
                extra_kwargs["user_id"] = user_id

            call_kwargs: Dict[str, Any] = {
                "model": self._model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.0,
                "max_tokens": 2000,
                **extra_kwargs,
            }

            if tools:
                call_kwargs["tools"] = self._convert_mcp_tools_to_openai(tools)

            response = await self._client.chat.completions.create(**call_kwargs)
            message = response.choices[0].message
            content_text = message.content or ""
            tool_calls: List[LlmToolCall] = []

            if getattr(message, "tool_calls", None):
                for tc in message.tool_calls:
                    fn_name = tc.function.name
                    fn_args_raw = tc.function.arguments
                    try:

                        fn_args = json.loads(fn_args_raw) if isinstance(fn_args_raw, str) else fn_args_raw
                    except Exception:
                        fn_args = {}
                    tool_calls.append(LlmToolCall(name=fn_name, arguments=fn_args))

            return LlmDecision(
                text=content_text if content_text else None,
                tool_calls=tool_calls,
            )
        except Exception as e:
            logger.error("Error generando decisión con Bedrock LLM: %s", e, exc_info=True)
            return LlmDecision(
                text="Ocurrió un error al procesar tu solicitud técnica. Por favor intentá nuevamente.",
                tool_calls=[],
            )