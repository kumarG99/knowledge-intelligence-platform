
from app.services.pdf_extraction import ExtractedPage
from app.services.text_chunking import chunk_pages


def test_chunk_pages_preserves_page_numbers_and_overlap():
    pages = [
        ExtractedPage(
            page_number=1,
            text="Alpha bravo charlie delta echo foxtrot golf hotel",
        ),
        ExtractedPage(
            page_number=2,
            text="India juliet kilo lima",
        ),
    ]

    chunks = chunk_pages(
        pages,
        chunk_size=25,
        overlap=5,
    )

    assert len(chunks) > 2

    assert chunks[0].page_number == 1
    assert chunks[0].chunk_index == 0

    assert any(chunk.page_number == 2 for chunk in chunks)

    assert all(len(chunk.content) <= 25 for chunk in chunks)

    assert "Alpha" in chunks[0].content
