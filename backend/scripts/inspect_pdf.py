
import argparse
from pathlib import Path

from app.services.pdf_extraction import extract_pdf_text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect text extracted from an uploaded PDF."
    )
    parser.add_argument(
        "file_path",
        type=Path,
        help="Path to a PDF file",
    )

    args = parser.parse_args()

    result = extract_pdf_text(args.file_path)

    print("\n=== PDF EXTRACTION RESULT ===")
    print(f"File: {args.file_path.name}")
    print(f"Total pages: {result.page_count}")
    print(f"Total characters: {len(result.full_text)}")

    for page in result.pages:
        print(f"\n--- PAGE {page.page_number} ---")
        print(page.text[:1000] or "[No extractable text]")

    print("\n=== END OF EXTRACTION ===")


if __name__ == "__main__":
    main()
