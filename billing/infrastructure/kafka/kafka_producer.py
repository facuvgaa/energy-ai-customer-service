from datetime import datetime, timezone
import json
import logging
import os
from aiokafka import AIOKafkaProducer


logger = logging.getLogger(__name__)


class KafkaBillingProducer:
    def __init__(self, bootstrap_servers: str = None, output_topic: str ="chat.outgoing.response"):
        self._bootstrap_servers = bootstrap_servers or os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self._output_topic = output_topic
        self._producer: AIOKafkaProducer | None = None


    async def start(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await self._producer.start()
        logger.info("Kafka producer de Billing iniciado exitosamente.")

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()
            logger.info("Kafka producer de Billing detenido.")
            
    async def publish_response(self, session_id: str, user_id: str, response_text: str) -> None:
        payload = {
            "session_id": session_id,
            "user_id": user_id,
            "content": response_text,
            "source": "billing",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self._producer.send_and_wait(
            topic=self._output_topic,
            value=payload,
            key=session_id.encode("utf-8"),
        )
        logger.info("Respuesta publicada en '%s' (session=%s)", self._output_topic, session_id)
