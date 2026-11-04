from domain.port.consulting_context_repository_port import ConsultingContextRepositoryPort
from domain.port.consulting_llm_port import ConsultingLlmPort
from domain.port.knowledge_retriever_port import KnowledgeRetrieverPort
from domain.models.consulting_context_model import ConsultingContextModel
from application.commands.command import Command
import logging

logger = logging.getLogger(__name__)

class ProcessConsultingMessage:
    def __init__(
        self, 
        consulting_context: ConsultingContextRepositoryPort,   
        consulting_llm: ConsultingLlmPort,
        knowledge: KnowledgeRetrieverPort,
    ):
        self._consulting_context = consulting_context
        self._consulting_llm = consulting_llm
        self._knowledge = knowledge

    async def execute(self, command: Command)-> str:
        context = await self._consulting_context.get_by_session(command.session_id)

        if not context:
            logger.info("Iniciando nuevo contexto para la sesión %s (user=%s)", command.session_id, command.user_id)
            context =   ConsultingContextModel(
                session_id=command.session_id,
                user_id=command.user_id,
            )

        context.messages.append({"role": "user", "content": command.content})


        chunks = await self._knowledge.retrieve(query=command.content, limit= 4)

        result = await self._consulting_llm.generate_response(
            query=command.content,
            context_chunks=chunks,
            chat_history=context.messages,
        )

        context.messages.append({"role":"assistant", "content": result.response_text})

        await self._consulting_context.save(context)

        return result.response_text