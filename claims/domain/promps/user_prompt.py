from typing import Dict, Any, List

def BUILD_TECHNICAL_CLAIM_USER_PROMPT(state: Dict[str, Any], context, tools: List[Any] = None) -> str:
    """Genera el prompt dinámico para el turno actual con historial, contexto técnico y fotos."""
    user_message = state.get("user_message", "")
    tool_results = state.get("tool_results", [])

    service_number = getattr(context, "service_number", None)
    service_numbers = getattr(context, "service_numbers", [])
    address = getattr(context, "address", None)
    photos_url = getattr(context, "photos_url", None)
    messages = getattr(context, "messages", [])
    last_claim = getattr(context, "last_claim", None)

    # Últimos 8 mensajes para contexto conversacional
    history_str = ""
    for m in messages[-8:]:
        role = "Cliente" if m.get("role") == "user" else "Asistente"
        history_str += f"- {role}: {m.get('content')}\n"

    # Herramientas ejecutadas en este turno
    tools_executed_str = ""
    if tool_results:
        for idx, tr in enumerate(tool_results, 1):
            tools_executed_str += (
                f"  {idx}. Tool `{tr.get('tool')}` con args {tr.get('args')}:\n"
                f"     Resultado: {tr.get('result')}\n"
            )
    else:
        tools_executed_str = "  Ninguna herramienta ejecutada todavía en este turno."

    last_claim_str = (
        f"ID={last_claim.get('claim_id')}, Estado={last_claim.get('status')}, Categoría={last_claim.get('category')}"
        if isinstance(last_claim, dict)
        else (str(last_claim) if last_claim else "Ninguno registrado en esta sesión")
    )

    return f"""
Historial reciente de la conversación:
{history_str or "    (Inicio de la conversación)"}

Mensaje actual del usuario: "{user_message}"

Datos técnicos y de contexto disponibles:
- Suministros asociados al usuario: {service_numbers or "No especificado"}
- Suministro activo: {service_number or "No identificado aún"}
- Dirección o ubicación física: {address or "No informada aún"}
- Foto adjunta en la sesión: {photos_url or "Ninguna"}
- Último reclamo generado en sesión: {last_claim_str}

Herramientas ejecutadas en este turno:
{tools_executed_str}

Instrucciones para este turno:
- Si el usuario reportó cables caídos, postes o fuego, recordale mantener distancia de seguridad.
- Si faltan datos clave como la dirección exacta para un reclamo en vía pública, pedila de forma clara y directa.
- Si ya contás con la información requerida, utilizá la herramienta para registrar el reclamo técnico.
"""

