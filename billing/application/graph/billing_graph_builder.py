from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from domain.ports.llm_provider_port import LLMProviderPort
from domain.ports.mcp_tool_provider_port import MCPToolProviderPort
from application.state.billing_state import BillingState
from billing.infrastructure.promps.billing_system_prompt import BILLING_SYSTEM_PROMPT


class BillingGraphBuilder:

    def __init__(self, llm_provider: LLMProviderPort, mcp_provider: MCPToolProviderPort):
        self._llm_provider = llm_provider
        self._mcp_provider = mcp_provider

    async def build(self):

        tools = await self._mcp_provider.get_tools()

        base_model = self._llm_provider.get_chat_model()

        model_with_tools = base_model.bind_tools()

        async def call_model(state: BillingState):

            messages = list(state['messages'])

            if not messages or not isinstance(messages[0], SystemMessage):
                messages = [SystemMessage(content=BILLING_SYSTEM_PROMPT)] + messages

            response = await model_with_tools.invoke(messages)
            return {"messages": [response]}

        def should_continue (state: BillingState)-> Literal["tools", END]:
            last_message = state["messages"][-1]
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "tools"
            return END

        workflow = StateGraph(BillingState)

        workflow.add_node("agents", call_model)
        workflow.add_node("tools", ToolNode(tools))

        workflow.set_entry_point("agent")

        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                END: END
            }
        )
        workflow.add_edge("tools", "agent")

        return workflow.compile()