"""Tests for the document question-answering API."""

import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.services.llm import LLMError
from app.services.rag import RAGResponse, RAGSource


def test_ask_returns_answer_and_sources(client: TestClient, db_session: Session):
    """A successful request returns the generated answer and citations."""

    organization = Organization(name="Ask API Test Organization")
    db_session.add(organization)
    db_session.commit()
    db_session.refresh(organization)

    document_id = uuid.uuid4()

    mock_result = RAGResponse(
        answer="The upload limit is 10 MiB. [1]",
        sources=[
            RAGSource(
                document_id=document_id,
                filename="upload-policy.pdf",
                page_number=2,
                chunk_index=0,
                similarity=0.91,
            )
        ],
        model="qwen2.5:3b",
        input_tokens=100,
        output_tokens=20,
        duration_seconds=2.5,
    )

    with patch(
        "app.api.routes.ask.answer_question",
        return_value=mock_result,
    ) as mock_answer:
        response = client.post(
            f"/api/v1/organizations/{organization.id}/ask",
            json={
                "question": "What is the upload limit?",
                "limit": 5,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == "The upload limit is 10 MiB. [1]"
    assert data["model"] == "qwen2.5:3b"
    assert data["sources"][0]["document_id"] == str(document_id)
    assert data["sources"][0]["filename"] == "upload-policy.pdf"
    assert data["sources"][0]["page_number"] == 2
    assert data["usage"]["input_tokens"] == 100
    assert data["usage"]["output_tokens"] == 20

    mock_answer.assert_called_once_with(
        db=db_session,
        organization_id=organization.id,
        question="What is the upload limit?",
        limit=5,
    )


def test_ask_rejects_blank_question(client: TestClient, db_session: Session):
    """Whitespace-only questions must be rejected."""

    organization = Organization(name="Blank Question Test")
    db_session.add(organization)
    db_session.commit()

    response = client.post(
        f"/api/v1/organizations/{organization.id}/ask",
        json={"question": "   "},
    )

    assert response.status_code == 422


def test_ask_rejects_invalid_limit(client: TestClient, db_session: Session):
    """Retrieval limits above the maximum must be rejected."""

    organization = Organization(name="Invalid Limit Test")
    db_session.add(organization)
    db_session.commit()

    response = client.post(
        f"/api/v1/organizations/{organization.id}/ask",
        json={
            "question": "What is KIP?",
            "limit": 21,
        },
    )

    assert response.status_code == 422


def test_ask_returns_404_for_unknown_organization(client: TestClient):
    """Unknown organizations must return HTTP 404."""

    response = client.post(
        f"/api/v1/organizations/{uuid.uuid4()}/ask",
        json={"question": "What is KIP?"},
    )

    assert response.status_code == 404


def test_ask_handles_ollama_failure(client: TestClient, db_session: Session):
    """Ollama failures must produce HTTP 503 without leaking details."""

    organization = Organization(name="Ollama Failure Test")
    db_session.add(organization)
    db_session.commit()

    with patch(
        "app.api.routes.ask.answer_question",
        side_effect=LLMError("Cannot connect to Ollama."),
    ):
        response = client.post(
            f"/api/v1/organizations/{organization.id}/ask",
            json={"question": "What is the upload limit?"},
        )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Question-answering service is temporarily unavailable."
    )
    assert "Cannot connect to Ollama" not in response.text
