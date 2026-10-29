import json
import logging
import os
from typing import Optional, List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

try:
    from langfuse.openai import AsyncOpenAI
except ImportError:
    from openai import AsyncOpenAI

from domain.ports.llm_provider_port import LlmProviderPort
from domain.models.llm_decision_model import LlmDecision, LlmToolCall

# Carga claims/.env o .env del proyecto
env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv()



logger = logging.getLogger(__name__)


class BedrockLlmAdapter(LlmProviderPort):
    def __init__(self, model_id: Optional[str] = None):
        self._model = model_id or os.getenv("OPENAI_MODEL", "openai.gpt-oss-120b")
        self._client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://bedrock-mantle.us-east-2.api.aws/v1"),
        )

    def _convert_mcp_tools_to_openai(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convierte los schemas de tools de MCP al formato function calling de OpenAI."""
        openai_tools = []
        for t in tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": t.get("name"),
                    "description": t.get("description", ""),
                    "parameters": t.get("input_schema", {"type": "object", "properties": {}}),
                }
            })
        return openai_tools

    async def generate_decision(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        name: str = "claims-assistant",
    ) -> LlmDecision:
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
            choice = response.choices[0]
            message = choice.message
            content_text = message.content or ""

            tool_calls: List[LlmToolCall] = []

            # 1. Native Tool Calls de la API
            if getattr(message, "tool_calls", None):
                for tc in message.tool_calls:
                    fn_name = tc.function.name
                    fn_args_raw = tc.function.arguments
                    try:
                        fn_args = json.loads(fn_args_raw) if isinstance(fn_args_raw, str) else fn_args_raw
                    except Exception:
                        fn_args = {}
                    tool_calls.append(LlmToolCall(name=fn_name, arguments=fn_args))

            # 2. Fallback si el modelo devolvió un JSON en el cuerpo del texto
            if not tool_calls and content_text.strip().startswith("{") and content_text.strip().endswith("}"):
                try:
                    parsed = json.loads(content_text.strip())
                    if "tool" in parsed and parsed.get("tool"):
                        tool_calls.append(LlmToolCall(
                            name=parsed["tool"],
                            arguments=parsed.get("args") or {},
                        ))
                        content_text = parsed.get("response") or ""
                except Exception:
                    pass

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
