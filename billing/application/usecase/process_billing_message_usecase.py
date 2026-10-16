from billing.domain.ports.storage_port import StoragePort
from domain.ports.billing_context_repository_port import BillingContextRepositoryPort
from domain.ports.billing_assistand_port import BillingAssistandPort
from domain.ports.document_extractor_port import DocumentExtractorPort
from domain.models.billing_context_model import  BillingContextModel
from typing import Optional
import logging

logger = logging.getLogger('use_case')
logger.setLevel(logging.DEBUG)

class ProcessBillingMessageUsecase:
    def __init__(
        self, 
        repository: BillingContextRepositoryPort,
        assistant:  BillingAssistandPort,
        extractor:  DocumentExtractorPort,
        storage:    StoragePort,
        ):
        self._repostitory = repository
        self._assistant = assistant
        self._extractor = extractor
        self._storage = storage

    async def execute(self, session_id: str, user_id: str, content:str, image_bytes: Optional[bytes] = None, filename: Optional[str]=None)-> str:

        context = await self._repostitory.get_by_session_id(session_id)

        if not context:
            logger.info("iniciando un nuevo contexto para la session %s (user=%s)", session_id, user_id)

            context = BillingContextModel(session_id=session_id)

        if image_bytes:

            name = filename or f"doc_{session_id}.jpg"
            image_url = await self._storage.upload(image_bytes, name)
            logger.info("Document save in storage: %s", image_url)

            doc = await self._extractor.extract_from_image(image_bytes)
            logger.info("document classifi with : %s", doc.document_type)

            if doc.service_number and not context.service_number:
                context.service_number = doc.service_number

            content += f"\n[El usuario adjuntó un documento tipo {doc.document_type.value}: " \
                       f"suministro={doc.service_number}, monto={doc.amount}, ref={doc.transaction_id}]"

            response_text, updated_context = await self._assistant.process_message(
                user_message=content,
                context=context
            )

            await self._repostitory.save(updated_context)

            return response_text