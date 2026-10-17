from abc import ABC, abstractmethod
from typing import Any

class LlmProviderPort(ABC):

    @abstractmethod
    def get_chat_model(self, system_prompt: str, user_prompt: str)-> str:
        """Returns the instance of the language model compatible with LangGraph
        (e.g., BaseChatModel), without coupling the domain to the specific SDK."""
        """
        Retorna la instancia del modelo de lenguaje compatible con LangGraph
        (ej: BaseChatModel), sin acoplar el dominio al SDK concreto.
        """
        pass
