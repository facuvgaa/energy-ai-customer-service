import json

def USER_PROMPT(state: dict, context, tools: list) -> str:
    """Genera el prompt del sistema para el flujo de facturación."""
    
    # Extraemos los datos de forma segura
    user_message = state.get("user_message", "")
    tool_result = state.get("tool_result")
    
    service_number = getattr(context, "service_number", None)
    account = getattr(context, "account", None)
    
    return f"""
    Mensaje del usuario: {user_message}
    
    Datos actuales de la sesión:
    - Suministro (service_number): {service_number}
    - Cuenta cargada: {account}
    - Resultado de herramienta recién ejecutada: {tool_result}
    
    Herramientas MCP disponibles:
    {json.dumps(tools, ensure_ascii=False, indent=2)}
    
    Respondé ÚNICAMENTE con un JSON válido con este formato:
    {{
        "service_number_detected": "string si el usuario mencionó su número de suministro o null",
        "tool_to_call": "nombre de la tool si necesitás consultar datos Y todavía no hay tool_result, o null",
        "tool_args": {{"param": "valor"}} o null,
        "response": "respuesta cordial al usuario si ya no necesitás llamar ninguna tool, o null"
    }}
    """