from typing import Annotated, Optional, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class BillingState(TypedDict):

    messages: Annotated[Sequence[BaseMessage], add_messages]

    session_id: str
    user_id: str 
    service_number: Optional[str]