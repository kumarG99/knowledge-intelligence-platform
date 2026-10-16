
from dataclasses import dataclass

from app.services.pdf_extraction import ExtractedPage


@dataclass(frozen=True)
class TextChunk:
    page_number: int
    chunk_index: int
    content: str


def chunk_pages(
    pages: list[ExtractedPage],
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[TextChunk]:
    """
    Split extracted PDF pages into overlapping text chunks.

    Each chunk retains its original page number.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size."
        )

    chunks: list[TextChunk] = []

    for page in pages:
        text = " ".join(page.text.split())

        if not text:
            continue

        start = 0
        chunk_index = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))

            # Prefer splitting at a word boundary.
            if end < len(text):
                last_space = text.rfind(" ", start, end)

                if last_space > start:
                    end = last_space

            content = text[start:end].strip()

            if content:
                chunks.append(
                    TextChunk(
                        page_number=page.page_number,
                        chunk_index=chunk_index,
                        content=content,
                    )
                )
                chunk_index += 1

            if end >= len(text):
                break

            # Advance while retaining overlapping context.
            next_start = end - overlap

            # Ensure forward progress even with long words.
            start = max(start + 1, next_start)

    return chunks
