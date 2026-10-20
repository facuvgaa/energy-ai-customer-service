DOCUMENT_EXTRACTOR_PROMPT = """Analizá la imagen adjunta y determiná si es:
- Una factura eléctrica (INVOICE)
- Un comprobante de pago (PAYMENT_RECEIPT)
- Una foto de un desperfecto/reclamo técnico como medidor roto, poste o cable caído (TECHNICAL_DAMAGE)
- Otro documento (UNKNOWN)

Extraé únicamente un objeto JSON válido con la siguiente estructura exacta (usá null si un campo no es visible):
{
  "document_type": "INVOICE" | "PAYMENT_RECEIPT" | "TECHNICAL_DAMAGE" | "UNKNOWN",
  "service_number": "string o null",
  "amount": float o null,
  "document_date": "YYYY-MM-DD o null",
  "transaction_id": "string o null",
  "invoice_id": "string o null",
  "description": "breve descripción de lo que se ve en la imagen"
}
No agregues bloques markdown ni texto adicional, solo el JSON puro.
"""

