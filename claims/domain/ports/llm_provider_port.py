from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from domain.models.llm_decision_model import LlmDecision


class LlmProviderPort(ABC):
    @abstractmethod
    async def generate_decision(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        name: str = "claims-assistant",
    ) -> LlmDecision:
        """
        Consulta al LLM con las herramientas disponibles y devuelve un LlmDecision normalizado
        (independiente de si abajo corre OpenAI, Bedrock, Gemini o Claude).
        """
        pass

