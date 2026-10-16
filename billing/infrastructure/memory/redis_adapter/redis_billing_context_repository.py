import json
import redis.asyncio as redis
from typing import Optional

from domain.models.billing_context_model import BillingContextModel
from domain.models.billing_account_model import BillingAccountModel
from domain.models.invoice_model import  InvoiceModel, InvoiceStatus
from domain.ports.billing_context_repository_port import BillingContextRepositoryPort

from datetime import date

class RedisBillingContextRepository(BillingContextRepositoryPort):
    def __init__(self, redis_url: str ="redis://localhost:6379", ttl_seconds: int = 3600):
        self._client = redis.from_url(redis_url, decode_responses=True)
        self._ttl = ttl_seconds

    async def save(self, context: BillingContextModel) -> None:
        key = f"billing:context:{context.session_id}"

        data = {
            "session_id": context.session_id,
            "user_id": context.user_id,
            "service_number": context.service_number,
            "is_autenticated": context.is_autenticated,
            "account": None,
        }

        if context.account:
            data["account"] = {
                "service_number": context.account.service_number,
                "hold_name": context.account.hold_name,
                "address": context.account.address,
                "invoices": [
                    {
                        "invoice_id": inv.invoice_id,
                        "service_number": inv.service_number,
                        "period": inv.period,
                        "amount": inv.amount,
                        "due_date": inv.due_date.isoformat(),
                        "status": inv.status.value,
                        "download_url": inv.download_url,
                    }
                    for inv in context.account.invoices
                ],
            }

        await self._client.setex(key, self._ttl, json.dumps(data))

    async def get_by_session_id(self, session_id: str) -> Optional[BillingContextModel]:

        key = f"billing:context:{session_id}"
        raw = await self._client.get(key)
        if not raw:
            return None
        data = json.loads(raw)
        account = None
        if data.get("account"):
            acc_data = data["account"]
            invoices = [
                InvoiceModel(
                    invoice_id=inv["invoice_id"],
                    service_number=inv["service_number"],
                    period=inv["period"],
                    amount=inv["amount"],
                    due_date=date.fromisoformat(inv["due_date"]),
                    status=InvoiceStatus(inv["status"]),
                    download_url=inv.get("download_url"),
                )
                for inv in acc_data.get("invoices", [])
            ]
            account = BillingAccountModel(
                service_number=acc_data["service_number"],
                hold_name=acc_data["hold_name"],
                address=acc_data["address"],
                invoices=invoices,
            )
        return BillingContextModel(
            session_id=data["session_id"],
            user_id=data["user_id"],
            service_number=data.get("service_number"),
            account=account,
            is_autenticated=data.get("is_autenticated", False),
        )