import logging
from application.command.process_billing_message_command import ProcessBillingMessageCommand
from domain.models.billing_context_model import BillingContextModel
from domain.ports.billing_assistand_port import BillingAssistandPort
from domain.ports.billing_context_repository_port import BillingContextRepositoryPort

logger = logging.getLogger("use_case")
logger.setLevel(logging.DEBUG)


class ProcessBillingMessageUsecase:

    def __init__(
        self,
        repository: BillingContextRepositoryPort,
        assistant: BillingAssistandPort,
    ):
        self._repository = repository
        self._assistant = assistant

    async def execute(self, command: ProcessBillingMessageCommand) -> str:
        context = await self._repository.get_by_session_id(command.session_id)

        if not context:
            logger.info(
                "Iniciando un nuevo contexto para la session %s (user=%s)",
                command.session_id,
                command.user_id,
            )
            context = BillingContextModel(
                session_id=command.session_id,
                user_id=command.user_id,
                is_autenticated=command.is_authenticated,
            )

        user_message = command.content

        if command.extracted_document:
            doc = command.extracted_document
            service_num = doc.get("service_number")
            if service_num and not context.service_number:
                context.service_number = str(service_num)

            user_message += (
                f"\n[Documento procesado por Vision ({doc.get('document_type')}): "
                f"suministro={service_num}, monto={doc.get('amount')}, "
                f"ref={doc.get('transaction_id')}, url={doc.get('image_url')}]"
            )

        response_text, updated_context = await self._assistant.process_message(
            user_message=user_message,
            context=context,
        )

        await self._repository.save(updated_context)

        return response_text