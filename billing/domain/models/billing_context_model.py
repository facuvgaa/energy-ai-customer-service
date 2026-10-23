from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from domain.models.billing_account_model import BillingAccountModel

@dataclass
class BillingContextModel:
    session_id: str 
    user_id: str 
    service_number: Optional[str] = None
    account: Optional[BillingAccountModel] = None
    is_autenticated: bool = False
    service_numbers: List[str] = field(default_factory=list)
    messages: List[Dict[str, str]] = field(default_factory=list)
    last_receipt: Optional[Dict[str, Any]] = None

    