import json
import logging
from typing import Optional
import redis.asyncio as redis

from domain.models.claim_context_model import ClaimContextModel
from domain.ports.claim_context_repository_port import ClaimContextRepositoryPort

logger = logging.getLogger(__name__)


class RedisClaimContextRepository(ClaimContextRepositoryPort):
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        ttl_seconds: int = 3600,
    ):
        self._client = redis.from_url(redis_url, decode_responses=True)
        self._ttl = ttl_seconds

    async def save(self, context: ClaimContextModel) -> None:
        key = f"claims:context:{context.session_id}"

        data = {
            "session_id": context.session_id,
            "user_id": context.user_id,
            "service_numbers": context.service_numbers,
            "service_number": context.service_number,
            "address": context.address,
            "messages": context.messages[-20:],
            "last_claim": context.last_claim,
            "photos_url": context.photos_url,
        }

        try:
            await self._client.setex(key, self._ttl, json.dumps(data))
        except Exception as e:
            logger.error("Error guardando contexto en Redis para %s: %s", key, e)

    async def get_by_session_id(self, session_id: str) -> Optional[ClaimContextModel]:
        key = f"claims:context:{session_id}"
        try:
            raw = await self._client.get(key)
            if not raw:
                return None

            data = json.loads(raw)
            return ClaimContextModel(
                session_id=data["session_id"],
                user_id=data["user_id"],
                service_numbers=data.get("service_numbers", []),
                service_number=data.get("service_number"),
                address=data.get("address"),
                messages=data.get("messages", []),
                last_claim=data.get("last_claim"),
                photos_url=data.get("photos_url"),
            )
        except Exception as e:
            logger.error("Error recuperando contexto de Redis para %s: %s", key, e)
            return None

    async def close(self) -> None:
        await self._client.aclose()