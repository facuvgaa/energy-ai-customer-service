import asyncio
import logging
import os
import signal
from application.usecase.classify_and_route_usecase import RouteUnclassifiedMessageUseCase
from infraestructure.llm.llm_factory.llm_factory import LLMFactory
from infraestructure.kafka.kafka_producer import KafkaPublisherAdapter
from infraestructure.kafka.kafka_consumer import KafkaUnclassifiedConsumer

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("App")

async def main():
    logger.info("Iniciando servicio de enrutamiento...")
    classifier = LLMFactory.get_classifier()


    producer = KafkaPublisherAdapter()
    await producer.start()


    use_case = RouteUnclassifiedMessageUseCase(
        classifier=classifier,
        publisher=producer
    )


    consumer = KafkaUnclassifiedConsumer(use_case=use_case)
    consumer_task = asyncio.create_task(consumer.start())


    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def signal_handler():
        logger.info("Señal recibida, apagando el servicio...")
        consumer.stop()
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    try:

        await stop_event.wait()
    finally:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.error("Excepción en consumer_task durante shutdown: %s", exc)

        try:
            await producer.stop()
        except Exception as exc:
            logger.error("Error cerrando producer: %s", exc)

        logger.info("Servicio detenido limpiamente.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass