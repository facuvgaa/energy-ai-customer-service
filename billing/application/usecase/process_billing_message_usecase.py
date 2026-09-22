from langchain_core.messages import HumanMessage
from application.graph.billing_graph_builder import BillingGraphBuilder

class ProcessBillingMessageUseCase:

    def __init__(self, graph_builder: BillingGraphBuilder):
        self._graph_builder = BillingGraphBuilder
        self_compile_graph = None

    async def execute(self, session_id : str, user_id: str, content: str) -> str:
        if self._compile_graph is None:
            self._compole_graph = await self._graph_builder.build()

        initial_state = {
        "messages": [HumanMessage(content=content)],
        "session_id": session_id,
        "user_id": user_id,
        "service_number": None
        }

        final_state = await self._compiled_graph.ainvoke(initial_state)

        last_message = final_state["messages"][-1]
        return last_message.content