from dataclasses import dataclass
from typing import Optional
from enum import Enum
from datetime import date


class DocumentType(str, Enum):
    INVOICE = "INVOICE"
    PAYMENT_RECEIPT = "PAYMENT_RECEIPT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ExtractedDocumentModel:
    document_type: DocumentType
    service_number: Optional[str] = None
    amount: Optional[float] = None
    document_date: Optional[date] = None
    transaction_id: Optional[str] = None
    invoice_id: Optional[str] = None 