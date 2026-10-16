
import uuid
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.organization import Organization


def test_upload_pdf_success(client: TestClient, db_session: Session):
    organization = Organization(name="Upload Test Organization")
    db_session.add(organization)
    db_session.commit()
    db_session.refresh(organization)

    response = client.post(
        f"/api/v1/organizations/{organization.id}/documents",
        files={
            "file": (
                "sample.pdf",
                b"%PDF-1.4\nsample content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201
    assert response.json()["filename"] == "sample.pdf"

    document_id = uuid.UUID(response.json()["id"])
    document = db_session.get(Document, document_id)

    assert document is not None
    assert document.organization_id == organization.id

    Path(document.storage_path).unlink(missing_ok=True)


def test_upload_rejects_invalid_pdf(client: TestClient, db_session: Session):
    organization = Organization(name="Invalid PDF Test")
    db_session.add(organization)
    db_session.commit()
    db_session.refresh(organization)

    response = client.post(
        f"/api/v1/organizations/{organization.id}/documents",
        files={
            "file": (
                "invalid.pdf",
                b"not a real PDF",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid PDF file."


def test_upload_cleans_file_on_database_failure(
    client: TestClient,
    db_session: Session,
):
    organization = Organization(name="Failure Test Organization")
    db_session.add(organization)
    db_session.commit()
    db_session.refresh(organization)

    fake_path = Path("uploads") / f"{uuid.uuid4()}.pdf"

    async def fake_save_pdf(file):
        fake_path.parent.mkdir(parents=True, exist_ok=True)
        fake_path.write_bytes(b"%PDF-1.4\nsample")
        return str(fake_path)

    with (
        patch("app.api.routes.documents.save_pdf", side_effect=fake_save_pdf),
        patch.object(Session, "commit", side_effect=RuntimeError("DB failure")),
    ):
        response = client.post(
            f"/api/v1/organizations/{organization.id}/documents",
            files={
                "file": (
                    "sample.pdf",
                    b"%PDF-1.4\nsample",
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 500
    assert not fake_path.exists()


def test_list_documents_only_returns_organization_documents(
    client: TestClient,
    db_session: Session,
):
    organization_a = Organization(name="Organization A")
    organization_b = Organization(name="Organization B")

    db_session.add_all([organization_a, organization_b])
    db_session.commit()

    db_session.refresh(organization_a)
    db_session.refresh(organization_b)

    document_a = Document(
        organization_id=organization_a.id,
        filename="organization-a.pdf",
        content_type="application/pdf",
        storage_path="test/a.pdf",
    )

    document_b = Document(
        organization_id=organization_b.id,
        filename="organization-b.pdf",
        content_type="application/pdf",
        storage_path="test/b.pdf",
    )

    db_session.add_all([document_a, document_b])
    db_session.commit()

    response = client.get(
        f"/api/v1/organizations/{organization_a.id}/documents"
    )

    assert response.status_code == 200

    filenames = [
        document["filename"]
        for document in response.json()
    ]

    assert filenames == ["organization-a.pdf"]
