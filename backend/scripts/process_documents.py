
import argparse

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.document import Document
from app.services.document_processing import process_document


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract and store text from uploaded PDFs."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all documents in the database.",
    )

    args = parser.parse_args()

    if not args.all:
        parser.error("Specify --all to process existing documents.")

    with SessionLocal() as db:
        documents = db.scalars(
            select(Document).order_by(Document.created_at)
        ).all()

        print(f"Found {len(documents)} document(s).")

        succeeded = 0
        failed = 0

        for document in documents:
            print(f"\nProcessing: {document.filename}")

            try:
                page_count = process_document(db, document.id)

                print(f"  Success: {page_count} page(s) stored.")
                succeeded += 1

            except Exception as exc:
                db.rollback()
                print(f"  Failed: {type(exc).__name__}: {exc}")
                failed += 1

        print("\n=== PROCESSING SUMMARY ===")
        print(f"Successful: {succeeded}")
        print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
