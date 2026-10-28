from abc import ABC, abstractmethod
from typing import Optional, List
from domain.models.claim_model import ClaimModel

class ClaimRepositoryPort(ABC):
    @abstractmethod
    async def save (self, claim: ClaimModel)->ClaimModel:
        """Guarda o actualiza un reclamo en el sistema/base de datos."""
        """Save or update a claim in the system/database."""
        pass

    @abstractmethod
    async def find_by_id(self, claim_id: str)->Optional[ClaimModel]:
        """Busca un reclamo por su ID único."""
        """Search for a claim by your unique ID."""
        pass

    @abstractmethod
    async def find_by_service_number(self, service_number: str) -> List[ClaimModel]:
        """Recupera el historial de reclamos asociados a un número de suministro."""
        """Retrieves the claims history associated with a supply number"""
        pass