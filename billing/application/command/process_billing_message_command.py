from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ProcessBillingMessageCommand:
    session_id: str
    user_id: str
    content: str
    image_bytes: Optional[bytes] = None
    filename: Optional[str] = None

