DOCUMENT_EXTRACTOR_PROMPT = """Analizá la imagen adjunta y determiná si es una factura eléctrica (INVOICE), un comprobante de pago (PAYMENT_RECEIPT) u otro documento (UNKNOWN).
Extraé únicamente un objeto JSON válido con la siguiente estructura exacta (usá null si un campo no es visible):
{
  "document_type": "INVOICE" | "PAYMENT_RECEIPT" | "UNKNOWN",
  "service_number": "string o null",
  "amount": float o null,
  "document_date": "YYYY-MM-DD o null",
  "transaction_id": "string o null",
  "invoice_id": "string o null"
}
No agregues bloques markdown ni texto adicional, solo el JSON puro.
"""