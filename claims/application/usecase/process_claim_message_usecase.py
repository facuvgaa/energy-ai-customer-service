import logging
from application.command.claims_command import ClaimCommand
from domain.models.claim_context_model import ClaimContextModel
from domain.ports.claim_assistant_port import ClaimAssistantPort
from domain.ports.claim_repository_port import ClaimRepositoryPort
from domain.ports.claim_context_repository_port import ClaimContextRepositoryPort

logger = logging.getLogger("usecase_claims")


class ProcessClaimMessageUsecase:
    def __init__(
        self,
        repository: ClaimRepositoryPort,
        assistant: ClaimAssistantPort,
        context_repository: ClaimContextRepositoryPort,
    ):
        self._repository = repository
        self._assistant = assistant
        self._context_repository = context_repository

    async def execute(self, command: ClaimCommand) -> str:
        context = await self._context_repository.get_by_session_id(command.session_id)

        if not context:
            logger.info("Iniciando nuevo contexto para la sesión %s (user=%s)", command.session_id, command.user_id)
            context = ClaimContextModel(
                session_id=command.session_id,
                user_id=command.user_id,
                service_numbers=command.service_numbers,
                photos_url=command.photo_url,
            )
            if len(command.service_numbers) == 1:
                context.service_number = command.service_numbers[0]
        elif command.service_numbers and not context.service_numbers:
            context.service_numbers = command.service_numbers

        user_message = command.content


        if command.extracted_document:
            doc = command.extracted_document
            if doc.get("image_url"):
                context.photos_url = doc.get("image_url")

            if doc.get("service_number") and not context.service_number:
                context.service_number = str(doc.get("service_number"))

            vision_desc = doc.get("description", "Sin descripción")

            user_message += (
                f"\n[Foto adjunta analizada por Vision AI: "
                f"Tipo={doc.get('document_type')}, "
                f"Daño detectado={vision_desc}, "
                f"URL={doc.get('image_url')}]"
            )


        context.messages.append({"role": "user", "content": user_message})

        result = await self._assistant.process_message(
            user_message=user_message,
            context=context,
        )

        if result.create_claim:
            await self._repository.save(result.create_claim)
            logger.info("Reclamo técnico guardado en BD con ID: %s", result.create_claim.claim_id)

        context.messages.append({"role": "assistant", "content": result.response_text})

        await self._context_repository.save(context)

        return result.response_text
