import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.organization import Organization


@pytest.fixture
def pdf_document(db_session: Session, tmp_path: Path):
    """Create two organizations and one PDF owned by the first."""
    organization = Organization(name="PDF Viewer Test Organization")
    other_organization = Organization(name="Other PDF Test Organization")

    db_session.add_all([organization, other_organization])
    db_session.flush()

    pdf_content = b"%PDF-1.4\n%Test PDF content\n%%EOF\n"
    pdf_path = tmp_path / "test-document.pdf"
    pdf_path.write_bytes(pdf_content)

    document = Document(
        organization_id=organization.id,
        filename="test-document.pdf",
        content_type="application/pdf",
        storage_path=str(pdf_path),
    )

    db_session.add(document)
    db_session.commit()

    return {
        "organization_id": organization.id,
        "other_organization_id": other_organization.id,
        "document_id": document.id,
        "pdf_path": pdf_path,
        "pdf_content": pdf_content,
    }


def document_file_url(organization_id, document_id):
    return f"/api/v1/organizations/{organization_id}/documents/{document_id}/file"


def test_get_document_file_success(
    client: TestClient,
    pdf_document,
):
    response = client.get(
        document_file_url(
            pdf_document["organization_id"],
            pdf_document["document_id"],
        )
    )

    assert response.status_code == 200
    assert response.content == pdf_document["pdf_content"]
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"

    content_disposition = response.headers["content-disposition"]
    assert content_disposition.startswith("inline;")
    assert "test-document.pdf" in content_disposition


def test_get_document_file_not_found(
    client: TestClient,
    pdf_document,
):
    response = client.get(
        document_file_url(
            pdf_document["organization_id"],
            uuid.uuid4(),
        )
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found."


def test_get_document_file_rejects_other_organization(
    client: TestClient,
    pdf_document,
):
    response = client.get(
        document_file_url(
            pdf_document["other_organization_id"],
            pdf_document["document_id"],
        )
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found."


def test_get_document_file_missing_on_disk(
    client: TestClient,
    pdf_document,
):
    pdf_document["pdf_path"].unlink()

    response = client.get(
        document_file_url(
            pdf_document["organization_id"],
            pdf_document["document_id"],
        )
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Document file not found."


def test_get_document_file_rejects_invalid_document_id(
    client: TestClient,
    pdf_document,
):
    response = client.get(
        document_file_url(
            pdf_document["organization_id"],
            "not-a-valid-uuid",
        )
    )

    assert response.status_code == 422
