from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AnalyzeDocumentCommand:
    session_id: str
    image_bytes: bytes
    filename: Optional[str] = None
    content_type: str = "image/jpeg"

