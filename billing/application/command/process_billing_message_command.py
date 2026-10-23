from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ProcessBillingMessageCommand:
    session_id: str
    user_id: str
    content: str
    is_authenticated: bool = False
    service_numbers: list[str] = field(default_factory=list)
    extracted_document: Optional[Dict[str, Any]] = None
