from dataclasses import dataclass, field
from typing import List
@dataclass
class ConsultingResultModel:
    response_text: str
    sources: List[str] = field(default_factory=list)

    