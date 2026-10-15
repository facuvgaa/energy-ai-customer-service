from dataclasses import dataclass
from typing import Optional
from domain.models.billing_account_model import BillingAccountModel

@dataclass
class BillingContextModel:
    session_id: str 
    user_id: str 
    service_number: Optional[str] = None
    account: Optional[BillingAccountModel] = None
    is_autenticated: bool = False

    