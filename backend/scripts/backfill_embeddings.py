"""Generate embeddings for existing document chunks."""

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.document import Document  # noqa: F401
from app.models.document_chunk import DocumentChunk
from app.services.embeddings import embed_texts

BATCH_SIZE = 32


def backfill_embeddings() -> None:
    """Generate and save embeddings for chunks missing them."""
    total_updated = 0

    with SessionLocal() as db:
        while True:
            chunks = (
                db.execute(
                    select(DocumentChunk)
                    .where(DocumentChunk.embedding.is_(None))
                    .order_by(DocumentChunk.id)
                    .limit(BATCH_SIZE)
                )
                .scalars()
                .all()
            )

            if not chunks:
                break

            texts = [chunk.content for chunk in chunks]
            embeddings = embed_texts(texts)

            for chunk, embedding in zip(chunks, embeddings, strict=True):
                chunk.embedding = embedding

            db.commit()

            total_updated += len(chunks)
            print(f"Embedded {total_updated} chunks")

    print(f"Backfill complete. Updated {total_updated} chunks.")


if __name__ == "__main__":
    backfill_embeddings()
