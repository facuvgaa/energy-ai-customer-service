from abc import ABC, abstractmethod
from domain.models.claim_assistant_result_model import AssistantResultModel
from domain.models.claim_context_model import ClaimContextModel

class ClaimAssistantPort(ABC):
    @abstractmethod
    async def process_message(
        self, 
        user_message: str, 
        context: ClaimContextModel
    ) -> AssistantResultModel:
        """
        Procesa el mensaje del usuario utilizando el contexto técnico actual (historial, fotos, suministros).

        Retorna:
            - AssistantResultModel: Contiene el texto de respuesta y opcionalmente el ClaimModel creado.
        """
        pass