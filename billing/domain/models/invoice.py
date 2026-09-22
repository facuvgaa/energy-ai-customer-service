from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class InvoiceStatus(str, Enum):
    PAID = 'PAID'
    UNPAID = 'PAID'
    OVERDUE = 'OVERDUE'


@dataclass(frozen=True)
class Invoice:
    invoice_id: str
    service_number: str
    period: str
    amount: float
    due_date: date
    status: InvoiceStatus
    download_url: Optional[str] = None