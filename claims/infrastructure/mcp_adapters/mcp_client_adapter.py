import hashlib
import json
import logging
import os
from typing import Any, Dict, List, Optional
import redis.asyncio as redis
from mcp import ClientSession
from mcp.client.sse import sse_client
from domain.ports.mcp_tool_provider_port import McpToolProviderPort

logger = logging.getLogger(__name__)


class McpClientAdapter(McpToolProviderPort):
    def __init__(
        self,
        sse_url: str = os.getenv("MCP_SERVER_URL", "http://localhost:8080/sse"),
        redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379"),
        cache_ttl_seconds: int = 600,
    ):
        self._sse_url = sse_url
        self._redis = redis.from_url(redis_url, decode_responses=True)
        self._cache_ttl = cache_ttl_seconds
        self._tools_cache: Optional[List[Dict[str, Any]]] = None

    async def list_tool(self) -> List[Dict[str, Any]]:
        if self._tools_cache is not None:
            return self._tools_cache

        try:
            async with sse_client(self._sse_url) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    response = await session.list_tools()
                    self._tools_cache = [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "input_schema": getattr(tool, "input_schema", getattr(tool, "inputSchema", {})),
                        }
                        for tool in response.tools
                    ]
                    return self._tools_cache
        except Exception as e:
            logger.error("Error listando tools del servidor MCP (%s): %s", self._sse_url, e, exc_info=True)
            return []

    def _normalize_args(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        normalized = dict(args or {})
        if "service_number" in normalized and "serviceNumber" not in normalized:
            normalized["serviceNumber"] = normalized.pop("service_number")
        if "client_id" in normalized and "clientId" not in normalized:
            normalized["clientId"] = normalized.pop("client_id")
        if "claim_number" in normalized and "claimNumber" not in normalized:
            normalized["claimNumber"] = normalized.pop("claim_number")


        for key in ("serviceNumber", "claimNumber"):
            if key in normalized:
                try:
                    normalized[key] = int(normalized[key])
                except (ValueError, TypeError):
                    pass
        return normalized

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        arguments = self._normalize_args(tool_name, arguments)
        args_hash = hashlib.md5(
            json.dumps(arguments, sort_keys=True).encode("utf-8")
        ).hexdigest()
        cache_key = f"claims:mcp_cache:{tool_name}:{args_hash}"

        is_query = tool_name.lower().startswith(
            ("get", "list", "find", "check", "consultar")
        )
        if is_query:
            try:
                cached = await self._redis.get(cache_key)
                if cached:
                    logger.info("Cache HIT en Redis para tool MCP '%s'", tool_name)
                    return cached
            except Exception as e:
                logger.warning("Error leyendo cache de Redis para tool '%s': %s", tool_name, e)

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
                    output = "\n".join(texts)

                    if is_query and output:
                        try:
                            await self._redis.setex(cache_key, self._cache_ttl, output)
                        except Exception as e:
                            logger.warning("Error guardando cache en Redis para tool '%s': %s", tool_name, e)

                    return output
        except Exception as e:
            logger.error("Error ejecutando tool MCP '%s': %s", tool_name, e, exc_info=True)
            return f"Error al consultar la herramienta {tool_name}: {str(e)}"

