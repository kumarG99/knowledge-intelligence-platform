
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"


async def save_pdf(file: UploadFile) -> str:
    """Validate and save a PDF using a generated filename."""

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    # Read at most 10 MB + 1 byte to detect oversized uploads.
    content = await file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="PDF exceeds the 10 MB limit.",
        )

    # Check the actual file signature, not just its declared MIME type.
    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file.",
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    stored_filename = f"{uuid.uuid4()}.pdf"
    destination = UPLOAD_DIR / stored_filename

    destination.write_bytes(content)

    return str(destination)
