"""Tests for organization-scoped semantic search."""

import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.organization import Organization


def test_search_only_returns_organization_chunks(
    client: TestClient,
    db_session: Session,
):
    """Search must not return another organization's document chunks."""

    organization_a = Organization(name="Search Organization A")
    organization_b = Organization(name="Search Organization B")

    db_session.add_all([organization_a, organization_b])
    db_session.flush()

    document_a = Document(
        organization_id=organization_a.id,
        filename="organization-a.pdf",
        content_type="application/pdf",
        storage_path="test/search-a.pdf",
    )

    document_b = Document(
        organization_id=organization_b.id,
        filename="organization-b.pdf",
        content_type="application/pdf",
        storage_path="test/search-b.pdf",
    )

    db_session.add_all([document_a, document_b])
    db_session.flush()

    # Identical vectors deliberately make both chunks equally relevant.
    # Only the organization filter should determine which is visible.
    vector = [1.0] + [0.0] * 383

    chunk_a = DocumentChunk(
        document_id=document_a.id,
        page_number=1,
        chunk_index=0,
        content="Organization A private document.",
        embedding=vector,
    )

    chunk_b = DocumentChunk(
        document_id=document_b.id,
        page_number=1,
        chunk_index=0,
        content="Organization B private document.",
        embedding=vector,
    )

    db_session.add_all([chunk_a, chunk_b])
    db_session.commit()

    with patch(
        "app.services.semantic_search.embed_text",
        return_value=vector,
    ):
        response_a = client.get(
            f"/api/v1/organizations/{organization_a.id}/search",
            params={"q": "private document", "limit": 5},
        )

        response_b = client.get(
            f"/api/v1/organizations/{organization_b.id}/search",
            params={"q": "private document", "limit": 5},
        )

    assert response_a.status_code == 200
    assert response_b.status_code == 200

    results_a = response_a.json()["results"]
    results_b = response_b.json()["results"]

    assert len(results_a) == 1
    assert len(results_b) == 1

    assert results_a[0]["document_id"] == str(document_a.id)
    assert results_b[0]["document_id"] == str(document_b.id)

    assert "Organization B" not in results_a[0]["content"]
    assert "Organization A" not in results_b[0]["content"]


def test_search_rejects_blank_query(
    client: TestClient,
    db_session: Session,
):
    organization = Organization(name="Blank Query Organization")
    db_session.add(organization)
    db_session.commit()

    response = client.get(
        f"/api/v1/organizations/{organization.id}/search",
        params={"q": "   "},
    )

    assert response.status_code == 422


def test_search_rejects_invalid_limit(
    client: TestClient,
    db_session: Session,
):
    organization = Organization(name="Invalid Limit Organization")
    db_session.add(organization)
    db_session.commit()

    response = client.get(
        f"/api/v1/organizations/{organization.id}/search",
        params={"q": "test", "limit": 21},
    )

    assert response.status_code == 422


def test_search_returns_404_for_unknown_organization(
    client: TestClient,
):
    unknown_organization_id = uuid.uuid4()

    response = client.get(
        f"/api/v1/organizations/{unknown_organization_id}/search",
        params={"q": "test"},
    )

    assert response.status_code == 404
