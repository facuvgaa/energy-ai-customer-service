from dataclasses import asdict
import logging
import os
from fastapi import FastAPI, File, Form, UploadFile
import uvicorn
from application.command.analyze_document_command import AnalyzeDocumentCommand
from application.usecase.analyze_document_usecase import AnalyzeDocumentUsecase
from infrastructure.llm.llm_factory.llm_factory import VisionLLMFactory
from infrastructure.storage.minio_storage_adapter import MinioStorageAdapter

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = FastAPI(title="Vision Document Microservice")

storage_adapter = MinioStorageAdapter()
extractor_adapter = VisionLLMFactory.get_document_extractor()
analyze_use_case = AnalyzeDocumentUsecase(
    storage=storage_adapter,
    extractor=extractor_adapter,
)


@app.post("/vision/analyze")
async def analyze_document(
    session_id: str = Form(...),
    file: UploadFile = File(...),
):
    image_bytes = await file.read()
    command = AnalyzeDocumentCommand(
        session_id=session_id,
        image_bytes=image_bytes,
        filename=file.filename,
        content_type=file.content_type or "image/jpeg",
    )
    result = await analyze_use_case.execute(command)
    payload = asdict(result)
    if result.document_date:
        payload["document_date"] = result.document_date.isoformat()
    payload["document_type"] = result.document_type.value
    return payload


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("VISION_PORT", "8001")))

