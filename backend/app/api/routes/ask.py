"""API endpoint for retrieval-augmented question answering."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.organization import Organization
from app.services.llm import LLMError
from app.services.rag import answer_question

router = APIRouter(tags=["Question Answering"])


class AskRequest(BaseModel):
    """Input for document question answering."""

    question: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=5, ge=1, le=20)


@router.post("/organizations/{organization_id}/ask")
def ask_documents(
    organization_id: uuid.UUID,
    request: AskRequest,
    db: Session = Depends(get_db),
):
    """Answer a question using documents from one organization."""

    if not request.question.strip():
        raise HTTPException(
            status_code=422,
            detail="Question cannot be blank.",
        )

    organization = db.get(Organization, organization_id)

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found.",
        )

    try:
        result = answer_question(
            db=db,
            organization_id=organization_id,
            question=request.question,
            limit=request.limit,
        )
    except LLMError as exc:
        raise HTTPException(
            status_code=503,
            detail="Question-answering service is temporarily unavailable.",
        ) from exc

    return {
        "organization_id": organization_id,
        "question": request.question,
        "answer": result.answer,
        "sources": [
            {
                "document_id": source.document_id,
                "filename": source.filename,
                "page_number": source.page_number,
                "chunk_index": source.chunk_index,
                "similarity": source.similarity,
            }
            for source in result.sources
        ],
        "model": result.model,
        "usage": {
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "duration_seconds": result.duration_seconds,
        },
    }
