from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict
from domain.models.llm_decision_model import LlmDecision

class LlmProviderPort(ABC):

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: List[Dict[str, Any]],
        session_id: Optional[str] = None,
    ) -> LlmDecision:
        """Retorna la respuesta generada por el LLM."""
        pass
