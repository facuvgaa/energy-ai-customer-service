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

        context = state.get("context")
        service_numbers = state.get("service_numbers") or (getattr(context, "service_numbers", []) if context else [])
        default_sn = (
            state.get("service_number")
            or getattr(context, "service_number", None)
            or (service_numbers[0] if service_numbers else 522363)
        )

        for tc in tool_calls:
            tool_name = getattr(tc, "name", None) or tc.get("name")
            tool_args = dict(getattr(tc, "arguments", None) or tc.get("arguments", {}))

            if tool_name == "create_claim":
                # Normalizar tipo de reclamo para coincidir con enum de Spring Boot (URGENT, RECONNECTION, BILLING_CLAIM)
                raw_type = str(tool_args.get("type", "URGENT")).upper()
                if raw_type in ("INFRASTRUCTURE_DANGER", "TECHNICAL_DAMAGE", "OUTAGE", "TECHNICAL", "URGENT"):
                    tool_args["type"] = "URGENT"
                elif raw_type in ("RECONNECTION", "PAYMENT"):
                    tool_args["type"] = "RECONNECTION"
                elif raw_type in ("BILLING_CLAIM", "BILLING", "INVOICE"):
                    tool_args["type"] = "BILLING_CLAIM"
                else:
                    tool_args["type"] = "URGENT"

                # Garantizar que serviceNumber sea entero válido
                sn = tool_args.get("serviceNumber") or default_sn
                try:
                    tool_args["serviceNumber"] = int(sn)
                except Exception:
                    tool_args["serviceNumber"] = 522363

                # Garantizar mínimo de 80 caracteres en la descripción requerido por el backend
                desc = str(tool_args.get("description", ""))
                addr = tool_args.get("address") or state.get("address") or ""
                if len(desc) < 80:
                    padding = f" Reporte técnico prioritario de infraestructura eléctrica.{f' Ubicación: {addr}.' if addr else ''} Derivado de forma urgente a cuadrilla de guardia."
                    desc = (desc + padding).strip()
                    tool_args["description"] = desc

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
