import logging
from domain.ports.claim_assistant_port import ClaimAssistantPort
from domain.models.claim_context_model import ClaimContextModel
from infrastructure.worfflows.graphs.claim_graph_builder import ClaimGraphBuilder
from domain.models.claim_assistant_result_model import AssistantResultModel
from infrastructure.worfflows.states.claim_state import ClaimState
logger = logging.getLogger(__name__)


class LanggraphClaimAssistantAdapter(ClaimAssistantPort):
    def __init__(self, graph: ClaimGraphBuilder):
        self._graph = graph.build()

    async def process_message(self, user_message: str, context: ClaimContextModel) -> AssistantResultModel:
        initial_state: ClaimState = {
            "user_message": user_message,
            "session_id": context.session_id,
            "service_numbers": context.service_numbers,
            "photo_url": context.photos_url,
            "address": context.address,
            "tool_calls": None,
            "tool_results": [],
            "final_response": None,
            "created_claim": None,
            "context": context,
        }

        logger.info("Running claims graph for session_id=%s", context.session_id)

        final_state = await self._graph.ainvoke(initial_state)

        return AssistantResultModel(
            response_text=final_state.get("final_response") or "Tu solicitud ha sido procesada.",
            create_claim=None,  # El reclamo ya es creado directamente por el ToolNode vía MCP Spring Boot
        )