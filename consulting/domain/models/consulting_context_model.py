from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class ConsultingContextModel:
    session_id: str
    user_id: str
    messages: List[Dict[str, str]] = field(default_factory=list)