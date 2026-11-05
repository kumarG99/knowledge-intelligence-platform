"""Semantic search over organization-scoped document chunks."""

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.embeddings import embed_text


@dataclass
class SearchResult:
    """A document chunk returned by semantic search."""

    document_id: UUID
    page_number: int
    chunk_index: int
    content: str
    similarity: float


def search_chunks(
    db: Session,
    organization_id: UUID,
    query: str,
    limit: int = 5,
) -> list[SearchResult]:
    """Find the most relevant chunks belonging to one organization."""

    if not query.strip():
        return []

    if not 1 <= limit <= 20:
        raise ValueError("Search limit must be between 1 and 20")

    query_embedding = embed_text(query)

    distance = DocumentChunk.embedding.cosine_distance(query_embedding)

    statement = (
        select(DocumentChunk, distance.label("distance"))
        .join(Document, DocumentChunk.document_id == Document.id)
        .where(
            Document.organization_id == organization_id,
            DocumentChunk.embedding.is_not(None),
        )
        .order_by(distance, DocumentChunk.id)
        .limit(limit)
    )

    rows = db.execute(statement).all()

    return [
        SearchResult(
            document_id=chunk.document_id,
            page_number=chunk.page_number,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            similarity=1.0 - float(cosine_distance),
        )
        for chunk, cosine_distance in rows
    ]
