from langgraph.graph import StateGraph, START, END

from infrastructure.langgraph_workfows.state.billing_state import BillingState
from infrastructure.langgraph_workfows.nodes.billing_node import BillingNode


class BillingGraphBuilder:
    def __init__(self, nodes: BillingNode):
        self._nodes = nodes

    def _should_call_tool(self, state: BillingState):

        if state.get("tool_to_call"):
            return "tools"
        return END

    def build(self):

        graph = StateGraph(BillingState)

        graph.add_node("agent", self._nodes.agent_node)
        graph.add_node("tools", self._nodes.tool_node)

        graph.add_edge(START,"agent")

        graph.add_conditional_edges(
            "agent",
            self._should_call_tool,
            {
                "tools":"tools",
                END: END,
            },
        )

        graph.add_edge("tools","agent")

        return graph.compile()