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
                raw_text = response.text or "{}"
                clean_json = raw_text.strip()
                if "```" in clean_json:
                    for part in clean_json.split("```"):
                        p_strip = part.strip()
                        if p_strip.startswith("json"):
                            p_strip = p_strip[4:].strip()
                        if (p_strip.startswith("{") and p_strip.endswith("}")) or (p_strip.startswith("[") and p_strip.endswith("]")):
                            clean_json = p_strip
                            break

                raw_data = json.loads(clean_json)
                if isinstance(raw_data, list):
                    data = raw_data[0] if raw_data and isinstance(raw_data[0], dict) else {}
                elif isinstance(raw_data, dict):
                    data = raw_data
                else:
                    data = {}


                raw_type = str(data.get("document_type", "UNKNOWN")).upper().strip()
                try:
                    doc_type = DocumentType(raw_type)
                except ValueError:
                    doc_type = DocumentType.UNKNOWN


                doc_date = None
                if data.get("document_date"):
                    try:
                        doc_date = date.fromisoformat(str(data["document_date"]).strip())
                    except Exception:
                        doc_date = None


                parsed_amount = None
                raw_amount = data.get("amount")
                if raw_amount is not None:
                    try:
                        if isinstance(raw_amount, (int, float)):
                            parsed_amount = float(raw_amount)
                        else:
                            clean_amt = str(raw_amount).replace("$", "").replace(" ", "").replace(".", "").replace(",", ".")
                            parsed_amount = float(clean_amt)
                    except Exception:
                        parsed_amount = None

                return ExtractedDocumentModel(
                    document_type=doc_type,
                    service_number=str(data["service_number"]) if data.get("service_number") else None,
                    amount=parsed_amount,
                    document_date=doc_date,
                    transaction_id=str(data["transaction_id"]) if data.get("transaction_id") else None,
                    invoice_id=str(data["invoice_id"]) if data.get("invoice_id") else None,
                    description=data.get("description"),
                )
            except Exception as e:
                logger.warning("Error extrayendo con '%s' (%s), probando fallback...", model_name, e)

        return ExtractedDocumentModel(document_type=DocumentType.UNKNOWN)

