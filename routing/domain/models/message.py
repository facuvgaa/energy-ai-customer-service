from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

class WorkFlowTarget(str, Enum):
    TECHNICAL_CLAIM = "chat.workflow.technical"
    BILLING = "chat.workflow.billing"
    GENERAL_QUERY = "chat.workflow.general"
    UNKNOWN = "chat.workflow.unclassified"

@dataclass(frozen=True)
class IncomingMessage:
    session_id: str
    user_id: str
    content: str
    service_numbers: list[str] = field(default_factory=list)
    attachments: list[dict] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
