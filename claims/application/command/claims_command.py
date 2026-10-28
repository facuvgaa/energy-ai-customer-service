from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass(frozen=True)
class ClaimCommand:
    session_id: str
    user_id: str
    content: str
    service_numbers: List[str] = field(default_factory=list)
    photo_url: Optional[str] = None
    extracted_document: Optional[Dict[str, Any]] = None
    