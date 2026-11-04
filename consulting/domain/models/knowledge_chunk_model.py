from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class KnowledgeChunkModel:
    content: str
    source: str
    page: Optional[int] = None