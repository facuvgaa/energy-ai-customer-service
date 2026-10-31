import logging
from typing import Dict, Any
from domain.promps.technical_claim_system_prompt import TECHNICAL_CLAIM_SYSTEM_PROMPT
from domain.promps.user_prompt import BUILD_TECHNICAL_CLAIM_USER_PROMPT
from infrastructure.worfflows.states.claim_state import ClaimState

logger = logging.getLogger(__name__)

class AssistantNode:
    def __init__(self, llm_client, mcp_provider):
        self._llm = llm_client
        self._mcp = mcp_provider
    async def __call__(self, state: ClaimState)-> Dict[str, Any]:

        tools = await self._mcp.list_tool()

        user_prompt = BUILD_TECHNICAL_CLAIM_USER_PROMPT(
            state=state,
            context=state.get("context"),
            tools=tools
        )

        decision = await self._llm.generate_decision(
            system_prompt = TECHNICAL_CLAIM_SYSTEM_PROMPT,
            user_prompt = user_prompt,
            tools = tools,
            session_id = state.get("session_id"),
        )

        return {
            "tool_calls": decision.tool_calls if decision.tool_calls else None,
            "final_response": decision.text,
        }
