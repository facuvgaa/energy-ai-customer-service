import json

def USER_PROMPT(state: dict, context, tools: list) -> str:
    """Genera el prompt con contexto completo, historial y resultados acumulados de herramientas."""
    user_message = state.get("user_message", "")
    tool_results = state.get("tool_results", [])
    
    service_number = getattr(context, "service_number", None)
    service_numbers = getattr(context, "service_numbers", [])
    account = getattr(context, "account", None)
    messages = getattr(context, "messages", [])
    last_receipt = getattr(context, "last_receipt", None)
    
    history_str = ""
    for m in messages[-8:]:
        role = "Cliente" if m.get("role") == "user" else "Asistente"
        history_str += f"- {role}: {m.get('content')}\n"

    tools_executed_str = ""
    if tool_results:
        for idx, tr in enumerate(tool_results, 1):
            tools_executed_str += f"  {idx}. Tool `{tr.get('tool')}` con args {tr.get('args')}:\n     Resultado: {tr.get('result')}\n"
    else:
        tools_executed_str = "  Ninguna herramienta ejecutada todavía en este turno."

    receipt_info = (
        f"SÍ (Tipo={last_receipt.get('document_type')}, Monto=${last_receipt.get('amount')}, Ref={last_receipt.get('transaction_id')})"
        if last_receipt else "NINGUNO ADJUNTO EN ESTA SESIÓN"
    )

    return f"""
    Historial reciente de la conversación:
{history_str or "    (Inicio de conversación)"}

    Último mensaje recibido: "{user_message}"

    Datos del cliente y cuenta:
    - Suministros registrados en su perfil: {service_numbers or "No especificado"}
    - Suministro activo en la sesión: {service_number or "Ninguno aún"}
    - Comprobante de pago verificado por Vision: {receipt_info}

    Resultados de herramientas ejecutadas en este turno:
{tools_executed_str}

    Herramientas MCP disponibles:
    {json.dumps(tools, ensure_ascii=False, indent=2)}

    REGLAS DE ORO DE NEGOCIO (ESTRICTAS):
    1. RECONEXIÓN Y AVISO DE PAGO:
       - Para ejecutar `create_claim` con tipo "RECONNECTION" o prometer reconexión, es ESTRICTAMENTE OBLIGATORIO que exista un comprobante de pago verificado ("Comprobante de pago verificado por Vision" != NINGUNO) y que el monto cubra la deuda total del suministro.
       - Si el cliente dice "si te pago ahora", "ya te pago", "después pago", "prometo pagar", o pide un aviso de reconexión SIN haber adjuntado el comprobante de pago real:
         * NO llames a `create_claim`.
         * Explicále que para emitir el aviso de reconexión prioritario es indispensable que primero realice el pago y adjunte el comprobante (con el botón 📎 o pegándolo con Ctrl+V).
         * Apenas recibamos el comprobante por el monto adeudado, se generará el reclamo de reconexión.
    2. SUMINISTROS Y DIRECCIONES:
       - Si el cliente pregunta qué suministros tiene o pide ver sus direcciones, consultá `get_electric_service_by_number` y mostrale cada número con su dirección real.
    3. HERRAMIENTAS:
       - Si necesitás datos de un suministro y la tool para ese número NO figura en "Resultados de herramientas ejecutadas", llamala con "tool_to_call" y "tool_args".
       - Si ya figura en "Resultados de herramientas ejecutadas", NO la repitas; respondé al cliente en "response".
    4. RESPUESTA LIMPIA:
       - NUNCA incluyas frases de pensamiento interno como "We will call tool". Respondé únicamente el JSON válido.

    Respondé ÚNICAMENTE con un JSON válido con este formato:
    {{
        "service_number_detected": "string del suministro detectado o seleccionado, o null",
        "tool_to_call": "nombre de la herramienta si vas a invocar una NUEVA, o null",
        "tool_args": {{"param": "valor"}} o null,
        "response": "respuesta final al usuario en lenguaje natural (o null si vas a llamar a una herramienta)"
    }}
    """
