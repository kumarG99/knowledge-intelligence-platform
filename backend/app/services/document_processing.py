
import uuid

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_page import DocumentPage
from app.services.pdf_extraction import extract_pdf_text
from app.services.text_chunking import chunk_pages


def process_document(
    db: Session,
    document_id: uuid.UUID,
) -> int:
    """
    Extract PDF text and persist pages and chunks.

    Returns the number of pages processed.
    """

    document = db.get(Document, document_id)

    if document is None:
        raise ValueError("Document not found.")

    # Extract and chunk before changing any stored content.
    extracted = extract_pdf_text(document.storage_path)
    chunks = chunk_pages(extracted.pages)

    try:
        # Replace previously processed content.
        db.execute(
            delete(DocumentChunk).where(
                DocumentChunk.document_id == document_id
            )
        )
        db.execute(
            delete(DocumentPage).where(
                DocumentPage.document_id == document_id
            )
        )

        for page in extracted.pages:
            db.add(
                DocumentPage(
                    document_id=document_id,
                    page_number=page.page_number,
                    content=page.text,
                )
            )

        for chunk in chunks:
            db.add(
                DocumentChunk(
                    document_id=document_id,
                    page_number=chunk.page_number,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                )
            )

        db.commit()

    except Exception:
        db.rollback()
        raise

    return extracted.page_count
