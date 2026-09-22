from abc import ABC, abstractmethod
from domain.models.message import WorkFlowTarget

class IntentClassifierPort(ABC):
    @abstractmethod
    async def classify(self, text: str) -> WorkFlowTarget:
        """Analiza el texto y retorna el objetivo de workflow."""
        pass