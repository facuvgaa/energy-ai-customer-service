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

    async def agent_node(self, state: BillingState) -> dict:
        context = state['context']
        tools = await self._mcp.list_tool()
        iteration = state.get("iteration_count", 0) + 1
        tool_results = list(state.get("tool_results") or [])

        # Salvaguarda: máximo 4 iteraciones de herramientas por mensaje para evitar bucles infinitos
        if iteration > 4:
            logger.warning("Límite de iteraciones alcanzado en billing_node (%d). Forzando respuesta final.", iteration)
            return {
                "iteration_count": iteration,
                "tool_to_call": None,
                "tool_args": None,
            }

        user_prompt = USER_PROMPT(
            state=state, 
            context=context, 
            tools=tools
        )

        raw_output = await self._llm.generate(
            system_prompt=BILLING_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            session_id=context.session_id,
            user_id=context.user_id,
            name="billing-agent-node"
        )

        clean_json = raw_output.strip()
        if "```" in clean_json:
            for part in clean_json.split("```"):
                p_strip = part.strip()
                if p_strip.startswith("json"):
                    p_strip = p_strip[4:].strip()
                if p_strip.startswith("{") and p_strip.endswith("}"):
                    clean_json = p_strip
                    break

        if not (clean_json.startswith("{") and clean_json.endswith("}")):
            start_idx = clean_json.find("{")
            end_idx = clean_json.rfind("}")
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                clean_json = clean_json[start_idx:end_idx + 1]

        try:
            decision = json.loads(clean_json)
        except Exception:
            decision = {"response": raw_output}

        detected_sn = decision.get("service_number_detected")
        if detected_sn and not context.service_number:
            context.service_number = str(detected_sn)

        tool_to_call = decision.get("tool_to_call")
        tool_args = decision.get("tool_args") or {}
        available_tool_names = [t.get("name") for t in tools] if tools else []

        if tool_to_call and tool_to_call not in available_tool_names:
            tool_to_call = None

        # GUARDRAIL EN CÓDIGO: No permitir create_claim de RECONEXIÓN si no hay comprobante adjunto
        if tool_to_call == "create_claim" and str(tool_args.get("type")).upper() == "RECONNECTION":
            if not getattr(context, "last_receipt", None):
                logger.warning("Guardrail activado: Intento de generar reconexión sin comprobante adjunto en sesión %s", context.session_id)
                tool_to_call = None

        # Salvaguarda anti-loop: si esta misma tool con estos mismos argumentos ya fue ejecutada, NO repetir
        if tool_to_call:
            for prev_tr in tool_results:
                if prev_tr.get("tool") == tool_to_call and prev_tr.get("args") == tool_args:
                    logger.info("Herramienta '%s' con args %s ya fue ejecutada en este turno. Evitando bucle.", tool_to_call, tool_args)
                    tool_to_call = None
                    break

        response_msg = decision.get("response") or ""
        # Filtrar posibles leaks de texto tipo "We will call tool."
        if response_msg and (response_msg.lower().strip().startswith("we will call") or "{" in response_msg):
            response_msg = ""
        # Si no hay respuesta para el usuario y no hay más herramientas que ejecutar
        if not response_msg and not tool_to_call:
            followup_prompt = (
                f"Resultados de herramientas ejecutadas en este turno:\n"
                f"{json.dumps(tool_results, ensure_ascii=False, indent=2) if tool_results else 'Ninguna herramienta ejecutada'}\n\n"
                f"Mensaje del cliente: \"{state.get('user_message')}\"\n"
                f"Suministro activo: {context.service_number}\n"
                f"Comprobante recibido en el chat: {'SÍ' if getattr(context, 'last_receipt', None) else 'NO'}\n\n"
                f"Escribí una respuesta cordial, empática y clara en lenguaje natural directamente para el cliente. "
                f"Si el cliente pide un aviso o reclamo de reconexión sin haber adjuntado el comprobante de pago, "
                f"explicále que es necesario que primero realice el pago y adjunte la foto/captura del comprobante "
                f"para que podamos verificar que cubre la deuda y emitir la orden de reconexión de inmediato. "
                f"NO uses formato JSON, respondé directamente con el texto para el cliente."
            )
            try:
                raw_followup = await self._llm.generate(
                    system_prompt=BILLING_SYSTEM_PROMPT,
                    user_prompt=followup_prompt,
                    session_id=context.session_id,
                    user_id=context.user_id,
                    name="billing-followup-node"
                )
                cleaned_followup = raw_followup.strip()
                if cleaned_followup.startswith("{") and cleaned_followup.endswith("}"):
                    try:
                        parsed_followup = json.loads(cleaned_followup)
                        response_msg = parsed_followup.get("response") or cleaned_followup
                    except Exception:
                        response_msg = cleaned_followup
                else:
                    response_msg = cleaned_followup
            except Exception:
                response_msg = "Para emitir la orden de reconexión prioritaria, es necesario que primero envíes el comprobante de pago por el monto adeudado. Apenas lo adjuntes, emitimos el aviso de inmediato."

        return {
            "context": context,
            "iteration_count": iteration,
            "tool_to_call": tool_to_call,
            "tool_args": tool_args,
            "response": response_msg,
        }

    async def tool_node(self, state: BillingState) -> dict:
        tool_name = state["tool_to_call"]
        tool_args = state.get("tool_args") or {}

        logger.info("execute tool MCP: %s con args=%s", tool_name, tool_args)

        result = await self._mcp.call_tool(tool_name, tool_args)
        
        # Acumulamos el resultado en el historial de herramientas de este turno
        current_results = list(state.get("tool_results") or [])
        current_results.append({
            "tool": tool_name,
            "args": tool_args,
            "result": result
        })

        return {
            "tool_to_call": None,
            "tool_args": None,
            "tool_results": current_results,
        }
