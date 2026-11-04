from abc import ABC, abstractmethod
from domain.models.knowledge_chunk_model import KnowledgeChunkModel
from domain.models.consulting_result_model import ConsultingResultModel
from typing import List, Dict
class ConsultingLlmPort(ABC):
    
    @abstractmethod
    async def generate_response(self, query: str, context_chunks: List[KnowledgeChunkModel], chat_history: list[Dict[str, str]] )-> ConsultingResultModel:
        """Genera una respuesta fundamentada en los fragmentos de conocimiento."""
        pass