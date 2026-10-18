import logging
from domain.models.billing_context_model import BillingContextModel
from domain.ports.billing_assistand_port import BillingAssistandPort
from infrastructure.langgraph_workfows.graph.billing_graph_builder import BillingGraphBuilder
from infrastructure.langgraph_workfows.state.billing_state import  BillingState


logger = logging.getLogger(__name__)


class LanggraphBillingAssistantAdapter(BillingAssistandPort):
    def __init__(self, graph_builder: BillingGraphBuilder):

        self._graph = graph_builder.build()

    async def process_message(self, user_message: str, context: BillingContextModel)-> tuple[str, BillingContextModel]:
            
        initial_state: BillingState = {
            "user_message": user_message,
            "context": context,
            "tool_to_call":None,
            "tool_args": None,
            "tool_result": None,
            "response": "",
        }

        logger.info("Running billing graph for session_id=%s", context.session_id)

        final_state = await self._graph.ainvoke(initial_state)

        return final_state["response"], final_state["context"]
    