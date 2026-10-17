from abc import ABC, abstractmethod
from typing import List, Any, Dict


class McpToolProviderPort(ABC):

    @abstractmethod
    async def list_tool(self)-> List[Dict[str, Any]]:
        """Obtiene la lista de herramientas disponibles en el servidor MCP."""
        """Retrieves the list of tools available on the MCP server."""
        pass

    async def call_tool(self, tool_name:str, arguments: Dict[str,Any])-> str:
        """Ejecuta una herramienta en el servidor MCP y devuelve su resultado en texto/JSON."""
        """Run a tool on the MCP server and return its result in text/JSON."""
        pass