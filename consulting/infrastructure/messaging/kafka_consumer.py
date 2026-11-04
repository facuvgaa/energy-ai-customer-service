import asyncio
import json
import logging
import os
from aiokafka import AIOKafkaConsumer

from application.commands.command import Command
from application.use_case.process_consulting_message import ProcessConsultingMessage
from infrastructure.messaging.kafka_producer import KafkaConsultingProducer

logger = logging.getLogger(__name__)


class KafkaConsultingConsumer:
    def __init__(
        self,
        use_case: ProcessConsultingMessage,
        producer: KafkaConsultingProducer,
        bootstrap_servers: str = None,
        topic: str = "chat.workflow.general",
        group_id: str = "consulting-workflow-group",
        max_concurrency: int = 50,
    ):
        self._use_case = use_case
        self._producer = producer
        self._bootstrap_servers = bootstrap_servers or os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self._topic = topic
        self._group_id = group_id
        self._consumer: AIOKafkaConsumer | None = None
        self._running = False
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._active_tasks: set[asyncio.Task] = set()

    async def _process_record(self, record) -> None:
        async with self._semaphore:
            try:
                if record.value is None:
                    return

                raw_val = (
                    record.value.decode("utf-8")
                    if isinstance(record.value, (bytes, bytearray))
                    else record.value
                )
                data = json.loads(raw_val) if isinstance(raw_val, str) else raw_val

                command = Command(
                    session_id=str(data["session_id"]),
                    user_id=str(data.get("user_id", "")),
                    content=str(data.get("content", "")),
                )

                response_text = await self._use_case.execute(command)

                await self._producer.publish_response(
                    session_id=command.session_id,
                    user_id=command.user_id,
                    response_text=response_text,
                )

            except Exception as err:
                logger.error(
                    "Error procesando mensaje en Consulting (offset %s): %s",
                    record.offset,
                    err,
                    exc_info=True,
                )

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            self._topic,
            bootstrap_servers=self._bootstrap_servers,
            group_id=self._group_id,
            auto_offset_reset="latest",
            enable_auto_commit=True,
        )
        await self._consumer.start()
        self._running = True
        logger.info("Escuchando consultas comerciales en topic '%s'...", self._topic)

        try:
            async for record in self._consumer:
                if not self._running:
                    break
                task = asyncio.create_task(self._process_record(record))
                self._active_tasks.add(task)
                task.add_done_callback(self._active_tasks.discard)
        finally:
            if self._active_tasks:
                logger.info("Esperando que terminen %d consultas en curso...", len(self._active_tasks))
                await asyncio.gather(*self._active_tasks, return_exceptions=True)

    def stop(self) -> None:
        self._running = False
        if self._consumer:
            asyncio.create_task(self._consumer.stop())
        logger.info("Kafka consumer de Consulting detenido.")

