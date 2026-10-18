from domain.ports.mcp_tool_provider_port import McpToolProviderPort
import logging
import os
from mcp import ClientSession
from mcp.client.sse import sse_client
from dotenv import load_dotenv
from typing import Any, Dict, List

logger = logging.getLogger(__name__)



class McpClientAdapter(McpToolProviderPort):
    def __init__(self, sse_url: str = os.getenv("MCP_SERVER_URL", "http://localhost:8080/sse")):
        self._sse_url = sse_url

    async def list_tool(self)-> List[Dict[str, Any]]:

        try: 
            async with sse_client(self._sse_url) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    response = await session.list_tools()
                    return [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "input_schema": tool.inputSchema,
                        }
                        for tool in response.tools
                    ]
        except Exception as e:
            logger.error("Error listando tools del servidor MCP (%s): %s", self._sse_url, e, exc_info=True)
            return []

    async def call_tool(self, tool_name, arguments):
        try:
            async with sse_client(self._sse_url) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments=arguments)
                    texts = [
                        content.text
                        for content in result.content
                        if hasattr(content, "text")
                    ]
                    return "\n".join(texts)
        except Exception as e:
            logger.error("Error ejecutando tool MCP '%s': %s", tool_name, e, exc_info=True)
            return f"Error al consultar la herramienta {tool_name}: {str(e)}"