from abc import ABC, abstractmethod
from typing import Optional
from domain.models.consulting_context_model import ConsultingContextModel
class ConsultingContextRepositoryPor(ABC):
    @abstractmethod
    async def get_by_session(self, session_id: str)->Optional[ConsultingContextModel]:
        pass

    @abstractmethod
    async def save(self, context: ConsultingContextModel)-> None:
        pass