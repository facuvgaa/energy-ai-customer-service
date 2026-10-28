from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class ClaimContextModel:
    session_id: str
    user_id: str
    service_numbers: List[str] = field(default_factory=list)
    service_number: Optional[str] = None
    address: Optional[str] = None
    messages: List[Dict[str, str]] = field(default_factory=list)
    last_claim: Optional[Dict[str, Any]] = None
    photos_url: Optional[str] = None

