import asyncio
import logging
import os
import signal
from pathlib import Path
from dotenv import load_dotenv
from infrastructure.memory.redis_claim_context_adapter import RedisClaimContextRepository
from infrastructure.mcp_adapters.mcp_client_adapter import McpClientAdapter
from infrastructure.persistence.mcp_claim_repository_adapter import McpClaimRepositoryAdapter
from infrastructure.llm.providers.bedrock_llm_adapter import BedrockLlmAdapter

from infrastructure.worfflows.nodes.tool_node import ToolNode
from infrastructure.worfflows.nodes.assistant_node import AssistantNode
from infrastructure.worfflows.graphs.claim_graph_builder import ClaimGraphBuilder
from infrastructure.worfflows.langgraph_claim_assistant_adapter import LanggraphClaimAssistantAdapter

from application.usecase.process_claim_message_usecase import ProcessClaimMessageUsecase

from infrastructure.messaging.kafka_consumer import KafkaClaimConsumer
from infrastructure.messaging.kafka_producer import KafkaClaimProducer

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")
load_dotenv()


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ClaimsApp")


async def main():
    logger.info("init microservice of claims....")

    context_repository = RedisClaimContextRepository()

    mcp_client = McpClientAdapter()

    claim_repository = McpClaimRepositoryAdapter(mcp_client=mcp_client)

    llm_adapter = BedrockLlmAdapter()

    assistant_node = AssistantNode(llm_client=llm_adapter, mcp_provider=mcp_client)

    tool_node = ToolNode(mcp_provider=mcp_client)

    graph_builder = ClaimGraphBuilder(assistant_node=assistant_node, tool_node=tool_node)

    assistant_adapter = LanggraphClaimAssistantAdapter(graph=graph_builder)

    use_case = ProcessClaimMessageUsecase(
        repository=claim_repository,
        assistant= assistant_adapter,
        context_repository= context_repository,
    )

    producer = KafkaClaimProducer()
    await producer.start()

    consumer = KafkaClaimConsumer(use_case=use_case, producer=producer)
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
        await context_repository.close()
        logger.info("Claims apagado limpiamente.")



if __name__== "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass