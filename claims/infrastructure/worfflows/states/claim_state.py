from typing import TypedDict, Optional, List, Dict, Any


class ClaimState(TypedDict):
    user_message: str
    session_id: str
    service_numbers: List[str]
    photo_url: Optional[str]
    address: Optional[str]
    tool_calls: Optional[List[Dict[str, Any]]]  
    tool_results: List[Dict[str, Any]]
    final_response: Optional[str]
    created_claim: Optional[Dict[str, Any]]