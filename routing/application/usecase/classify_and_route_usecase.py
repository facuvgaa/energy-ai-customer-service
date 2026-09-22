import logging
from domain.models.message import IncomingMessage
from domain.ports.intent_classifier_port import IntentClassifierPort
from domain.ports.event_publisher_port import EventPusblisherPort

logger = logging.getLogger(__name__)


class RouteUnclassifiedMessageUseCase():
    def __init__(
            self,
            classifier: IntentClassifierPort,
            publisher: EventPusblisherPort     

    ):
        self._classifier = classifier
        self._publisher = publisher    

    async def execute(self, message: IncomingMessage)->None:
        logger.info("Procesando mensaje no clasificado (session_id=%s, user_id=%s)", message.session_id, message.user_id)
        target = await self._classifier.classify(message.content)
        logger.info("Intención clasificada: %s para sesión %s", target.value, message.session_id)

        await self._publisher.publish_to_workflow(target, message)

        await self._publisher.notify_session_routed(message.session_id, target)