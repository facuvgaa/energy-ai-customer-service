from datetime import datetime, timezone
import json
import logging
import os
from aiokafka import AIOKafkaConsumer
from domain.models.message import IncomingMessage
from application.usecase.classify_and_route_usecase import RouteUnclassifiedMessageUseCase

logger = logging.getLogger(__name__)


class KafkaUnclassifiedConsumer:
    def __init__(
        self,
        use_case: RouteUnclassifiedMessageUseCase,
        bootstrap_servers: str = None,
        topic: str = "chat.incoming.unclassified",
        group_id: str = "routing-engine-group"
    ):
        self._use_case = use_case
        self._bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
        )
        self._topic = topic
        self._group_id = group_id
        self._consumer: AIOKafkaConsumer | None = None
        self._running = False

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            self._topic,
            bootstrap_servers=self._bootstrap_servers,
            group_id=self._group_id,
            auto_offset_reset="latest",
            enable_auto_commit=True
        )
        await self._consumer.start()
        self._running = True
        logger.info("Escuchando mensajes en '%s'...", self._topic)

        try:
            async for record in self._consumer:
                if not self._running:
                    break
                try:
                    if record.value is None:
                        logger.warning("Mensaje vacío recibido en offset %s", record.offset)
                        continue

                    raw_val = record.value.decode("utf-8") if isinstance(record.value, (bytes, bytearray)) else record.value
                    data = json.loads(raw_val) if isinstance(raw_val, str) else raw_val

                    if not isinstance(data, dict):
                        logger.warning("El payload en offset %s no es un objeto JSON: %r", record.offset, data)
                        continue

                    raw_ts = data.get("timestamp")
                    ts = datetime.fromisoformat(raw_ts) if raw_ts else datetime.now(timezone.utc)
                    msg = IncomingMessage(
                        session_id=str(data["session_id"]),
                        user_id=str(data.get("user_id", "")),
                        content=str(data["content"]),
                        timestamp=ts
                    )
                    await self._use_case.execute(msg)
                except Exception as err:
                    logger.error("Error procesando mensaje en offset %s: %s", record.offset, err, exc_info=True)
        finally:
            await self._consumer.stop()

    def stop(self) -> None:
        logger.info("Deteniendo Kafka consumer...")
        self._running = False