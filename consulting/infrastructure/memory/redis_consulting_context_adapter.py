import json
import logging
import os
from typing import Optional
import redis.asyncio as aioredis
from domain.port.consulting_context_repository_port import ConsultingContextRepositoryPort
from domain.models.consulting_context_model import ConsultingContextModel

logger = logging.getLogger(__name__)


class RedisConsultingContextAdapter(ConsultingContextRepositoryPort):
    def __init__(self, redis_url: Optional[str] = None, ttl_seconds: int = 86400):
        self._redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._ttl = ttl_seconds
        self._redis = aioredis.from_url(self._redis_url, decode_responses=True)

    async def get_by_session(self, session_id: str)-> Optional[ConsultingContextModel]:

        key = f"consulting:session:{session_id}"
        try:
            data_raw = await self._redis.get(key)
            if not data_raw:
                return None

            data = json.loads(data_raw)

            return ConsultingContextModel(
                session_id=data["session_id"],
                user_id=data["user_id"],
                messages=data.get("messages",[]),
            )
        except Exception as e:
            logger.error(f"error {e}")
            return None

    async def save(self, context: ConsultingContextModel)-> None:

        key = f"consulting:session:{context.session_id}"

        
        data = {
            "session_id":context.session_id,
            "user_id": context.user_id,
            "messages": context.messages
        }

        try:
            await self._redis.setex(key, self._ttl, json.dumps(data))
        except Exception as e:
            logger.error("Error guardando contexto en Redis para %s: %s", key, e)

    async def close(self) -> None:
        await self._redis.close()
