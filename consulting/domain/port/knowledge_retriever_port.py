from abc import ABC, abstractmethod
from typing import List
from domain.models.knowledge_chunk_model import KnowledgeChunkModel
class KnowledgeRetrieverPort(ABC):
    @abstractmethod
    async def retrieve(self, query: str, limit: int=4)-> List[KnowledgeChunkModel]:
        """Recupera los fragmentos de conocimiento más relevantes para la consulta."""
        pass