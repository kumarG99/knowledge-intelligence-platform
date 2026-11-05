"""Tests for retrieval-augmented question answering."""

import uuid
from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.organization import Organization
from app.services.llm import LLMResponse
from app.services.rag import answer_question
from app.services.semantic_search import SearchResult


def test_rag_generates_answer_with_source(db_session: Session):
    """RAG should include retrieved context and return source metadata."""

    organization = Organization(name="RAG Test Organization")
    db_session.add(organization)
    db_session.commit()
    db_session.refresh(organization)

    document = Document(
        organization_id=organization.id,
        filename="upload-policy.pdf",
        content_type="application/pdf",
        storage_path="test/upload-policy.pdf",
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    search_result = SearchResult(
        document_id=document.id,
        page_number=2,
        chunk_index=0,
        content="The maximum PDF upload size is 10 MiB.",
        similarity=0.91,
    )

    llm_result = LLMResponse(
        answer="The maximum upload size is 10 MiB. [1]",
        model="qwen2.5:3b",
        input_tokens=100,
        output_tokens=20,
        duration_seconds=2.5,
    )

    with (
        patch(
            "app.services.rag.search_chunks",
            return_value=[search_result],
        ) as mock_search,
        patch(
            "app.services.rag.generate_answer",
            return_value=llm_result,
        ) as mock_llm,
    ):
        result = answer_question(
            db=db_session,
            organization_id=organization.id,
            question="What is the upload limit?",
        )

    assert result.answer == "The maximum upload size is 10 MiB. [1]"
    assert len(result.sources) == 1
    assert result.sources[0].document_id == document.id
    assert result.sources[0].filename == "upload-policy.pdf"
    assert result.sources[0].page_number == 2
    assert result.sources[0].similarity == 0.91
    assert result.model == "qwen2.5:3b"
    assert result.input_tokens == 100
    assert result.output_tokens == 20

    mock_search.assert_called_once_with(
        db=db_session,
        organization_id=organization.id,
        query="What is the upload limit?",
        limit=5,
    )

    llm_prompt = mock_llm.call_args.kwargs["prompt"]
    assert "upload-policy.pdf" in llm_prompt
    assert "The maximum PDF upload size is 10 MiB." in llm_prompt
    assert "What is the upload limit?" in llm_prompt


def test_rag_handles_no_search_results(db_session: Session):
    """No retrieved chunks should produce a fallback without calling Ollama."""

    with (
        patch(
            "app.services.rag.search_chunks",
            return_value=[],
        ),
        patch("app.services.rag.generate_answer") as mock_llm,
    ):
        result = answer_question(
            db=db_session,
            organization_id=uuid.uuid4(),
            question="What is the refund policy?",
        )

    assert result.answer == "I don't know based on the provided documents."
    assert result.sources == []
    assert result.model is None
    assert result.input_tokens == 0
    assert result.output_tokens == 0
    mock_llm.assert_not_called()


def test_rag_rejects_blank_question(db_session: Session):
    """Whitespace-only questions should be rejected."""

    with pytest.raises(ValueError, match="Question cannot be empty"):
        answer_question(
            db=db_session,
            organization_id=uuid.uuid4(),
            question="   ",
        )


def test_rag_rejects_invalid_limit(db_session: Session):
    """The retrieval limit must remain within the allowed range."""

    with pytest.raises(ValueError, match="Search limit"):
        answer_question(
            db=db_session,
            organization_id=uuid.uuid4(),
            question="What is KIP?",
            limit=21,
        )


def test_rag_does_not_include_other_organization_documents(db_session: Session):
    """Even unexpected search results must not expose another tenant's content."""

    organization_a = Organization(name="RAG Organization A")
    organization_b = Organization(name="RAG Organization B")

    db_session.add_all([organization_a, organization_b])
    db_session.commit()

    document_b = Document(
        organization_id=organization_b.id,
        filename="private-document.pdf",
        content_type="application/pdf",
        storage_path="test/private-document.pdf",
    )

    db_session.add(document_b)
    db_session.commit()

    unexpected_result = SearchResult(
        document_id=document_b.id,
        page_number=1,
        chunk_index=0,
        content="Confidential information belonging to Organization B.",
        similarity=0.99,
    )

    with (
        patch(
            "app.services.rag.search_chunks",
            return_value=[unexpected_result],
        ),
        patch("app.services.rag.generate_answer") as mock_llm,
    ):
        result = answer_question(
            db=db_session,
            organization_id=organization_a.id,
            question="What does the private document say?",
        )

    assert result.sources == []
    assert result.answer == "I don't know based on the provided documents."
    mock_llm.assert_not_called()
