from dataclasses import dataclass
from domain.models.claim_model import ClaimModel
from typing import Optional
@dataclass(frozen=True)
class AssistantResultModel:
    response_text: str
    create_claim: Optional[ClaimModel] = None