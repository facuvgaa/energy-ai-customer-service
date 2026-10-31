import logging
from infrastructure.worfflows.states.claim_state import ClaimState
from domain.ports.mcp_tool_provider_port import McpToolProviderPort
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ToolNode:
    def __init__(self, mcp_provider: McpToolProviderPort )-> Dict[str, Any]:
        self._mcp = mcp_provider

    async def __call__(self, state: ClaimState):

        tool_calls = state.get("tool_calls") or []
        current_results = list(state.get("tool_results")or [])
        created_claim = state.get("created_claim")

        for tc in tool_calls:
            tool_name = getattr(tc, "name", None) or tc.get("name")
            tool_args = getattr(tc, "arguments", None) or tc.get("arguments",{})

            logger.info("ejecutando herramientas MCP '%s' con args:%s", tool_name, tool_args)

            result_str = await self._mcp.call_tool(tool_name, tool_args)

            current_results.append({
                "tool": tool_name,
                "args": tool_args,
                "result": result_str,
            })

            if tool_name == "create_claim" and "CLM-" in str(result_str):

                created_claim = {
                    "raw_response": result_str,
                    "service_number": tool_args.get("serviceNumber"),
                    "description": tool_args.get("description"),
                    "type": tool_args.get("type"),
                }

        return {
            "tool_calls": None,
            "tool_results": current_results,
            "created_claim": created_claim,
        }
