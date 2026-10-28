from application.command.claims_command import ClaimCommand
from domain.ports.claim_assistant_port import ClaimAssistantPort
from domain.ports.claim_repository_port import ClaimRepositoryPort
from application.command.claims_command import ClaimCommand
from domain.ports.claim_context_repository_port import ClaimContextModel

class ProcessClaimMessageUsecase:
    def __init__(self, repository : ClaimRepositoryPort, assistant: ClaimAssistantPort, context: ClaimContextModel):
        self._repository = repository
        self._assistant = assistant
        self._context = context

    async def execute(self, command: ClaimCommand)-> str:
        context = await self._context.get_by_session(command.session_id)