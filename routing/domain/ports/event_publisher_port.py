from abc import ABC, abstractmethod
from domain.models.message import IncomingMessage, WorkFlowTarget


class EventPusblisherPort(ABC):
    @abstractmethod
    async def publish_to_workflow(self, target: WorkFlowTarget, message: IncomingMessage)-> None:
        """publish message int the appropriate topic"""
        """publica el mensaje en el topico correspondiente"""
        pass

    async def notify_session_routed(self, session_id: str, target:WorkFlowTarget )-> None:
        """Le avisa al Gateway (o a Redis) que esta sesión ya quedó fijada a un workflow."""
        """It notifies the Gateway (or Redis) that this session has already been assigned to a workflow."""
        pass