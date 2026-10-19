import base64
import json
import logging
import os
from aiokafka import AIOKafkaConsumer
from application.command.process_billing_message_command import ProcessBillingMessageCommand
from application.usecase.process_billing_message_usecase import ProcessBillingMessageUsecase
from infrastructure.kafka.kafka_producer import KafkaBillingProducer

logger = logging.getLogger(__name__)


class KafkaBillingConsumer:

    def __init__(
        self,
        use_case: ProcessBillingMessageUsecase,
        producer: KafkaBillingProducer,
        bootstrap_servers: str = None,
        topic: str = "chat.workflow.billing",
        group_id: str = "billing-workflow-group",
    ):
        self._use_case = use_case
        self._producer = producer
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
            enable_auto_commit=True,
        )
        await self._consumer.start()
        self._running = True
        logger.info("Escuchando mensajes de facturación en '%s'...", self._topic)

        try:
            async for record in self._consumer:
                if not self._running:
                    break
                try:
                    if record.value is None:
                        continue

                    raw_val = (
                        record.value.decode("utf-8")
                        if isinstance(record.value, (bytes, bytearray))
                        else record.value
                    )
                    data = json.loads(raw_val) if isinstance(raw_val, str) else raw_val

                    # Si viene una imagen en base64, la pasamos a bytes
                    image_b64 = data.get("image_base64")
                    image_bytes = base64.b64decode(image_b64) if image_b64 else None

                    # 1. Armamos el Command
                    command = ProcessBillingMessageCommand(
                        session_id=str(data["session_id"]),
                        user_id=str(data.get("user_id", "")),
                        content=str(data.get("content", "")),
                        image_bytes=image_bytes,
                        filename=data.get("filename"),
                    )

                    # 2. Ejecutamos el Caso de Uso
                    response_text = await self._use_case.execute(command)

                    # 3. Enviamos la respuesta al tópico de salida
                    await self._producer.publish_response(
                        session_id=command.session_id,
                        user_id=command.user_id,
                        response_text=response_text,
                    )

                except Exception as err:
                    logger.error(
                        "Error procesando mensaje en Billing (offset %s): %s",
                        record.offset,
                        err,
                        exc_info=True,
                    )
        finally:
            await self._consumer.stop()

    def stop(self) -> None:
        logger.info("Deteniendo Kafka consumer de Billing...")
        self._running = False