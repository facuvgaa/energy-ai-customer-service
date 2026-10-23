from typing import TypedDict, Optional, List, Dict, Any
from domain.models.billing_context_model import BillingContextModel


class BillingState(TypedDict):
    user_message: str
    context: BillingContextModel
    tool_to_call: Optional[str]
    tool_args: Optional[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    iteration_count: int
    response: str
