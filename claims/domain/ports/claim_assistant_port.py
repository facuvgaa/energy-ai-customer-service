from abc import ABC, abstractmethod
from typing import Optional
from domain.models.claim_assistant_result_model import AssistantResultModel

class ClaimAssistantPort(ABC):
    @abstractmethod
    async def process_message(self, user_message: str, session_id: str, photo_url: Optional[str] = None)-> AssistantResultModel:
        """
            Procesa el mensaje del usuario y analiza si corresponde crear o actualizar un reclamo técnico.
            Retorna:
                - str: Respuesta generada para mostrarle al usuario en el chat.
                - Optional[ClaimModel]: Si se identificó y generó un reclamo técnico, el modelo creado; si no, None.
        """
        """
            Processes the user's message and analyzes whether to create or update a technical support request.

            Returns:

                - str: Generated response to display to the user in the chat.

                - Optional[ClaimModel]: If a technical support request was identified and generated, the created model; otherwise, None.
        """
        pass