
import pymupdf
import pytest

from app.services.pdf_extraction import extract_pdf_text


def test_extract_pdf_text_preserves_page_numbers(tmp_path):
    pdf_path = tmp_path / "sample.pdf"

    pdf = pymupdf.open()

    page_one = pdf.new_page()
    page_one.insert_text((72, 72), "KIP supports document intelligence.")

    page_two = pdf.new_page()
    page_two.insert_text((72, 72), "Operations runbooks contain procedures.")

    pdf.save(pdf_path)
    pdf.close()

    result = extract_pdf_text(pdf_path)

    assert result.page_count == 2
    assert len(result.pages) == 2

    assert result.pages[0].page_number == 1
    assert "KIP supports document intelligence." in result.pages[0].text

    assert result.pages[1].page_number == 2
    assert "Operations runbooks contain procedures." in result.pages[1].text

    assert "KIP supports document intelligence." in result.full_text
    assert "Operations runbooks contain procedures." in result.full_text


def test_extract_pdf_text_rejects_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        extract_pdf_text(tmp_path / "missing.pdf")
