import json
import logging
import os
from aiokafka import AIOKafkaProducer
from domain.models.message import IncomingMessage, WorkFlowTarget
from domain.ports.event_publisher_port import EventPusblisherPort

logger = logging.getLogger(__name__)


class KafkaPublisherAdapter(EventPusblisherPort):
    def __init__(self, bootstrap_servers: str = None):
        self._bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
        )
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        await self._producer.start()
        logger.info("Kafka producer iniciado exitosamente.")

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()
            logger.info("Kafka producer detenido.")


    async def publish_to_workflow(self, topic: WorkFlowTarget, message: IncomingMessage) -> None:

        topic_name = topic.value if topic else WorkFlowTarget.UNKNOWN.value

        payload = {
            "session_id": message.session_id,
            "user_id": message.user_id,
            "content": message.content,
            "timestamp": message.timestamp.isoformat() if hasattr(message, "timestamp") and message.timestamp else None
        }

        await self._producer.send_and_wait(
            topic=topic_name,
            value=payload,
            key=message.session_id.encode("utf-8")
        )
        logger.info("Mensaje ruteado a '%s' para session: %s", topic_name, message.session_id)

    async def notify_session_routed(self, session_id: str, target: WorkFlowTarget) -> None:
    
        payload = {
            "session_id": session_id,
            "target_topic": target.value
        }
        await self._producer.send_and_wait(
            topic="chat.session.routed",
            value=payload,
            key=session_id.encode("utf-8")
        )
        logger.info("Notificada fijación de ruta: %s -> %s", session_id, target.value)

    async def update_session_route(self, session_id: str, topic: WorkFlowTarget) -> None:
        await self.notify_session_routed(session_id, topic)

