from dataclasses import dataclass, field
from typing import List
from domain.models.invoice import Invoice, InvoiceStatus



@dataclass
class BillingAccount:
    service_number: str 
    hold_name: str 
    address: str 
    invoices: List[Invoice] = field(default_factory=list)

    @property
    def total_debt(self)->float:
        return sum(inv.amount for inv in self.invoices if inv.status != InvoiceStatus.PAID)

    @property
    def has_overdue(self) -> bool:
        return any(inv.status == InvoiceStatus.OVERDUE for inv in self.invoices)

    @property
    def latest_invoice(self) -> Invoice | None:
        if not self.invoices:
            return None
        return sorted(self.invoices, key=lambda x: x.due_date, reverse=True)[0]