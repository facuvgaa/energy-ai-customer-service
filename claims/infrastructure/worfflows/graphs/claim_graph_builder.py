from langgraph.graph import START, END, StateGraph

from infrastructure.worfflows.nodes.assistant_node import AssistantNode
from infrastructure.worfflows.nodes.tool_node import ToolNode
from infrastructure.worfflows.states.claim_state import ClaimState

class ClaimGraphBuilder:
    def __init__(self, assistant_node: AssistantNode, tool_node: ToolNode):
        self._assitant_node= assistant_node
        self._tool_node = tool_node
    
    def _should_call_tool(self, state: ClaimState):

        if state.get("tool_calls"):
            return "tools"
        return END

    def build(self):

        graph = StateGraph(ClaimState)

        graph.add_node("agent", self._assitant_node)
        graph.add_node("tools", self._tool_node)

        graph.add_edge(START, "agent")

        graph.add_conditional_edges(
            "agent",
            self._should_call_tool,
            {
                "tools":"tools",
                END:END,
            },
        )

        graph.add_edge("tools","agent")

        return graph.compile()