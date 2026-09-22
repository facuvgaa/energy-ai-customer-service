from abc import ABC, abstractmethod
from typing import List, Any


class MCPToolProviderPort(ABC):

    @abstractmethod
    async def get_tools(self)-> List[Any]:
        """
        Obtiene del servidor MCP las tools disponibles (consultar saldo,
        descargar boleta, pagar) listas para bindear al modelo de LangGraph.
        """
        """
        Retrieves the available tools from the MCP server (check balance, 
        download receipt, pay) ready to bind to the LangGraph model.
        """
        pass