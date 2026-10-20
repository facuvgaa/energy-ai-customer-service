from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ProcessBillingMessageCommand:
    session_id: str
    user_id: str
    content: str
    is_authenticated: bool = False
    extracted_document: Optional[Dict[str, Any]] = None
