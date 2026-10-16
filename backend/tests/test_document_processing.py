
import uuid

import pymupdf
from sqlalchemy import select

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_page import DocumentPage
from app.models.organization import Organization
from app.services.document_processing import process_document


def test_process_document_saves_and_replaces_pages_and_chunks(
    db_session,
    tmp_path,
):
    organization = Organization(
        id=uuid.uuid4(),
        name="Processing Test Organization",
    )
    db_session.add(organization)
    db_session.flush()

    pdf_path = tmp_path / "processing-test.pdf"

    with pymupdf.open() as pdf:
        pdf.new_page().insert_text(
            (72, 72),
            "KIP document processing test.",
        )
        pdf.new_page().insert_text(
            (72, 72),
            "Second page contains searchable text.",
        )
        pdf.save(pdf_path)

    document = Document(
        id=uuid.uuid4(),
        organization_id=organization.id,
        filename="processing-test.pdf",
        content_type="application/pdf",
        storage_path=str(pdf_path),
    )

    db_session.add(document)
    db_session.commit()

    assert process_document(db_session, document.id) == 2

    pages = db_session.scalars(
        select(DocumentPage)
        .where(DocumentPage.document_id == document.id)
        .order_by(DocumentPage.page_number)
    ).all()

    assert len(pages) == 2
    assert "KIP document processing test." in pages[0].content
    assert "Second page" in pages[1].content

    chunks = db_session.scalars(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document.id)
        .order_by(
            DocumentChunk.page_number,
            DocumentChunk.chunk_index,
        )
    ).all()

    assert len(chunks) == 2
    assert chunks[0].page_number == 1
    assert chunks[0].chunk_index == 0
    assert "KIP document processing test." in chunks[0].content
    assert chunks[1].page_number == 2
    assert chunks[1].chunk_index == 0

    # Running the processor again must replace old records.
    assert process_document(db_session, document.id) == 2

    pages_after = db_session.scalars(
        select(DocumentPage).where(
            DocumentPage.document_id == document.id
        )
    ).all()

    chunks_after = db_session.scalars(
        select(DocumentChunk).where(
            DocumentChunk.document_id == document.id
        )
    ).all()

    assert len(pages_after) == 2
    assert len(chunks_after) == 2
