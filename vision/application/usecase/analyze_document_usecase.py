from dataclasses import replace
import logging
from application.command.analyze_document_command import AnalyzeDocumentCommand
from domain.models.extracted_document_model import ExtractedDocumentModel
from domain.ports.document_extractor_port import DocumentExtractorPort
from domain.ports.storage_port import StoragePort

logger = logging.getLogger(__name__)


class AnalyzeDocumentUsecase:

    def __init__(
        self,
        storage: StoragePort,
        extractor: DocumentExtractorPort,
    ):
        self._storage = storage
        self._extractor = extractor

    async def execute(self, command: AnalyzeDocumentCommand) -> ExtractedDocumentModel:
        name = command.filename or f"doc_{command.session_id}.jpg"
        image_url = await self._storage.upload(
            file_bytes=command.image_bytes,
            filename=name,
            content_type=command.content_type,
        )
        logger.info("Imagen guardada en MinIO: %s", image_url)

        extracted = await self._extractor.extract_from_image(command.image_bytes)
        logger.info("Documento clasificado por Vision como: %s", extracted.document_type)

        return replace(extracted, image_url=image_url)

