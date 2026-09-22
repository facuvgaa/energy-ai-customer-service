from dataclasses import dataclass
from typing import Optional
from domain.models.billing_account import BillingAccount

@dataclass
class BillingContext:
    session_id: str 
    user_id: str 
    service_number: Optional[str] = None
    account: Optional[BillingAccount] = None
    is_autenticated: bool = False

    