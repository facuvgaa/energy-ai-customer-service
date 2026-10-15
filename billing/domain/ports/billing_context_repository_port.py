from abc import ABC, abstractmethod
from typing import Optional
from domain.models.billing_context_model import BillingContextModel

class BillingContextRepositoryPort(ABC):
    @abstractmethod
    async def get_by_session_id(self, session_id: str)-> Optional[BillingContextModel]:
        """Recupera el contexto de la sesión desde el almacenamiento (ej: Redis)."""
        """Retrieve the session context from storage (e.g., Redis)."""
        pass

    @abstractmethod
    async def save(self, context: BillingContextModel)->None:
        """Guarda o actualiza el contexto de la sesión en el almacenamiento."""
        """Save or update the session context in storage."""
        pass