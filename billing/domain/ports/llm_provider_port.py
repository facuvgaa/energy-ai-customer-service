from abc import ABC, abstractmethod
from typing import Any

class LlmProviderPort(ABC):

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        session_id: str | None = None,
        user_id: str | None = None,
        name: str = "billing-assistant"
    ) -> str:
        """Retorna la respuesta generada por el LLM."""
        pass
