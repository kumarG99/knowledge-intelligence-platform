"""API endpoint for organization-scoped semantic search."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.organization import Organization
from app.services.semantic_search import search_chunks

router = APIRouter(tags=["Search"])


@router.get("/organizations/{organization_id}/search")
def search_documents(
    organization_id: uuid.UUID,
    q: str = Query(min_length=1, max_length=500),
    limit: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """Search embedded document chunks within an organization."""

    if not q.strip():
        raise HTTPException(
            status_code=422,
            detail="Search query cannot be blank.",
        )

    organization = db.get(Organization, organization_id)

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found.",
        )

    results = search_chunks(
        db=db,
        organization_id=organization_id,
        query=q,
        limit=limit,
    )

    return {
        "organization_id": organization_id,
        "query": q,
        "count": len(results),
        "results": [
            {
                "document_id": result.document_id,
                "page_number": result.page_number,
                "chunk_index": result.chunk_index,
                "content": result.content,
                "similarity": result.similarity,
            }
            for result in results
        ],
    }
