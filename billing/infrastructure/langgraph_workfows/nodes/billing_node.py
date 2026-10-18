import json
import logging
from domain.ports.llm_provider_port import LlmProviderPort
from domain.ports.mcp_tool_provider_port import McpToolProviderPort
from domain.promps.billing_system_prompt import BILLING_SYSTEM_PROMPT
from domain.promps.user_prompt import USER_PROMPT
from infrastructure.langgraph_workfows.state.billing_state import BillingState

logger = logging.getLogger(__name__)

class BillingNode:
    def __init__(self, llm: LlmProviderPort, mcp: McpToolProviderPort):
        self._llm = llm
        self._mcp = mcp 

    async def agent_node(self, state: BillingState)->dict:

        context = state['context']
        tools = await self._mcp.list_tool()

        user_prompt = USER_PROMPT(
        state=state, 
        context=context, 
        tools=tools
    )

        raw_output = await self._llm.generate(
            system_prompt=BILLING_SYSTEM_PROMPT,
            user_prompt = user_prompt,
        )

        clean_json = raw_output.strip().removeprefix("```json").removesuffix("```").strip()
        decision = json.loads(clean_json)


        if decision.get("service_number_detected") and not context.service_number:
            context.service_number = str(decision["service_number_detected"])


        return {
            "context": context,
            "tool_to_call": decision.get("tool_to_call"),
            "tool_args": decision.get("tool_args"),
            "response": decision.get("response") or "",
        }
    async def tool_node(self, state: BillingState)-> dict:
        tool_name = state["tool_to_call"]
        tool_args = state.get("tool_args") or {}

        logger.info("execute tool MCP: %s con args=%s", tool_name, tool_args)

        result = await self._mcp.call_tool(tool_name, tool_args)
        return {
            "tool_to_call": None,
            "tool_args": None,
            "tool_result": result,
        }
