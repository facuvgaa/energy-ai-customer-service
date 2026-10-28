from abc import ABC, abstractmethod
from typing import Optional
from domain.models.claim_context_model import ClaimContextModel

class ClaimContextRepositoryPort(ABC):
    @abstractmethod
    async def get_by_session_id(self, session_id: str) -> Optional[ClaimContextModel]:
        """Recupera el contexto de la sesión desde el almacenamiento (ej: Redis)."""
        pass

    @abstractmethod
    async def save(self, context: ClaimContextModel) -> None:
        """Guarda o actualiza el contexto de la sesión en el almacenamiento."""
        pass

