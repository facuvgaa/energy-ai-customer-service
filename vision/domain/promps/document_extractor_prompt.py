DOCUMENT_EXTRACTOR_PROMPT = """Analizá la imagen adjunta y determiná si es:
- Una factura eléctrica (INVOICE)
- Un comprobante de pago (PAYMENT_RECEIPT)
- Un daño o peligro en infraestructura eléctrica como cables caídos, poste quebrado, transformador o medidor dañado (TECHNICAL_DAMAGE)
- Otro documento o foto no relacionada (UNKNOWN)

Instrucciones para "description":
- Si es TECHNICAL_DAMAGE: Describí con precisión el desperfecto físico (ej: 'Poste de madera quebrado', 'Cable de media tensión cortado tocando el piso', 'Transformador humeando'). Aclará si representa PELIGRO INMINENTE (fuego, chispas, riesgo para peatones o vehículos).
- Si es INVOICE o PAYMENT_RECEIPT: Indicá brevemente el concepto o entidad (ej: 'Comprobante de transferencia por $15.890').

Extraé únicamente un objeto JSON válido con la siguiente estructura exacta (usá null si un campo no es visible):
{
  "document_type": "INVOICE" | "PAYMENT_RECEIPT" | "TECHNICAL_DAMAGE" | "UNKNOWN",
  "service_number": "string o null",
  "amount": float o null,
  "document_date": "YYYY-MM-DD o null",
  "transaction_id": "string o null",
  "invoice_id": "string o null",
  "description": "descripción detallada según las instrucciones"
}
No agregues bloques markdown ni texto adicional, solo el JSON puro.
"""


