import asyncio
import logging
import os
import signal
from application.usecase.process_billing_message_usecase import ProcessBillingMessageUsecase
from infrastructure.kafka.kafka_consumer import KafkaBillingConsumer
from infrastructure.kafka.kafka_producer import KafkaBillingProducer
from infrastructure.langgraph_workfows.langgraph_billing_assistant_adapter import LanggraphBillingAssistantAdapter
from infrastructure.langgraph_workfows.nodes.billing_node import BillingNode
from infrastructure.langgraph_workfows.graph.billing_graph_builder import BillingGraphBuilder
from infrastructure.llm.llm_factory.llm_factory import LLMFactory
from infrastructure.mcp_adapters.mcp_client_adapter import McpClientAdapter
from infrastructure.memory.redis_adapter.redis_billing_context_repository import RedisBillingContextRepository

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("BillingApp")


async def main():
    logger.info("Initializing Billing microservice...")

    repository = RedisBillingContextRepository()
    llm_provider = LLMFactory.get_llm_provider()
    mcp_client = McpClientAdapter()

    billing_nodes = BillingNode(llm=llm_provider, mcp=mcp_client)
    graph_builder = BillingGraphBuilder(nodes=billing_nodes)
    assistant = LanggraphBillingAssistantAdapter(graph_builder=graph_builder)

    use_case = ProcessBillingMessageUsecase(
        repository=repository,
        assistant=assistant,
    )

    producer = KafkaBillingProducer()
    await producer.start()

    consumer = KafkaBillingConsumer(use_case=use_case, producer=producer)
    consumer_task = asyncio.create_task(consumer.start())

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def signal_handler():
        logger.info("Signal received, shutting down Billing service...")
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
        await producer.stop()
        logger.info("Billing service stopped cleanly.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass