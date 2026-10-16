
from dataclasses import dataclass
from pathlib import Path

import pymupdf


@dataclass(frozen=True)
class ExtractedPage:
    page_number: int
    text: str


@dataclass(frozen=True)
class ExtractedDocument:
    page_count: int
    pages: list[ExtractedPage]
    full_text: str


def extract_pdf_text(file_path: str | Path) -> ExtractedDocument:
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {path}")

    pages: list[ExtractedPage] = []

    with pymupdf.open(path) as pdf:
        if not pdf.is_pdf:
            raise ValueError("The provided file is not a PDF.")

        for page_index, page in enumerate(pdf):
            text = page.get_text("text").strip()

            pages.append(
                ExtractedPage(
                    page_number=page_index + 1,
                    text=text,
                )
            )

    full_text = "\n\n".join(
        page.text for page in pages if page.text
    )

    return ExtractedDocument(
        page_count=len(pages),
        pages=pages,
        full_text=full_text,
    )
