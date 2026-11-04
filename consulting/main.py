from infrastructure.memory.redis_consulting_context_adapter import RedisConsultingContextAdapter
from infrastructure.adapter_retriever.chroma_knowledge_retriever_adapter import ChromaKnowledgeRetrieverAdapter
from infrastructure.llm.providers.bedrock.bedrock_consulting_llm_adapter import BedrockConsultingLlmAdapter
from application.use_case.process_consulting_message import ProcessConsultingMessage
from infrastructure.messaging.kafka_consumer import KafkaConsultingConsumer
from infrastructure.messaging.kafka_producer import KafkaConsultingProducer
import asyncio
import logging
import os
from pathlib import Path
import signal

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")
load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ConsultingApp")

async def main():
    logger.info("init microservice of consulting....")

    context_repo = RedisConsultingContextAdapter()
    knowledge_retriever = ChromaKnowledgeRetrieverAdapter()
    llm_adapter = BedrockConsultingLlmAdapter()

    use_case = ProcessConsultingMessage(
        consulting_context=context_repo,
        consulting_llm=llm_adapter,
        knowledge=knowledge_retriever,
    )

    producer = KafkaConsultingProducer()
    await producer.start()
    consumer = KafkaConsultingConsumer(use_case=use_case, producer=producer)
    consumer_task = asyncio.create_task(consumer.start())


    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()
    def signal_handler():
        logger.info("Señal de parada recibida...")
        consumer.stop()
        stop_event.set()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)
    try:
        await stop_event.wait()
    finally:
        consumer_task.cancel()
        await producer.stop()
        await context_repo.close()
        logger.info("Consulting apagado limpiamente.")
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass