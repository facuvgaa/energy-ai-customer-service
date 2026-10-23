from datetime import date
import json
import logging
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from domain.models.extracted_document_model import DocumentType, ExtractedDocumentModel
from domain.ports.document_extractor_port import DocumentExtractorPort
from domain.promps.document_extractor_prompt import DOCUMENT_EXTRACTOR_PROMPT

load_dotenv()
logger = logging.getLogger(__name__)

MODEL_GEMINI = os.getenv("MODEL_GEMINI", "gemini-3.5-flash-lite")


class GeminiDocumentExtractorAdapter(DocumentExtractorPort):
    def __init__(self, model_id: str = MODEL_GEMINI):
        self._model = model_id
        self._fallback_models = ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.8-flash"]
        self._client = genai.Client()

    async def extract_from_image(self, image_bytes: bytes) -> ExtractedDocumentModel:
        models_to_try = [self._model] + [m for m in self._fallback_models if m != self._model]
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/jpeg",
        )

        for model_name in models_to_try:
            try:
                response = await self._client.aio.models.generate_content(
                    model=model_name,
                    contents=[image_part, DOCUMENT_EXTRACTOR_PROMPT],
                    config=types.GenerateContentConfig(
                        temperature=0.0,
                        response_mime_type="application/json",
                    ),
                )
                data = json.loads(response.text)
                doc_date = (
                    date.fromisoformat(data["document_date"])
                    if data.get("document_date")
                    else None
                )

                return ExtractedDocumentModel(
                    document_type=DocumentType(data.get("document_type", "UNKNOWN")),
                    service_number=data.get("service_number"),
                    amount=float(data["amount"]) if data.get("amount") is not None else None,
                    document_date=doc_date,
                    transaction_id=data.get("transaction_id"),
                    invoice_id=data.get("invoice_id"),
                    description=data.get("description"),
                )
            except Exception as e:
                logger.warning("Error extrayendo con '%s' (%s), probando fallback...", model_name, e)

        return ExtractedDocumentModel(document_type=DocumentType.UNKNOWN)

