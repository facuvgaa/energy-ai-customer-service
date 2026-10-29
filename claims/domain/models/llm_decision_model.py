from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass(frozen=True)
class LlmToolCall:
    name: str
    arguments: Dict[str, Any]

@dataclass(frozen=True)
class LlmDecision:
    text: Optional[str] = None
    tool_calls: List[LlmToolCall] = field(default_factory=list)

