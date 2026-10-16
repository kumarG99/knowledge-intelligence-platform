
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.document import Document
from app.models.organization import Organization
from app.services.document_storage import save_pdf

router = APIRouter()


@router.post(
    "/organizations/{organization_id}/documents",
    status_code=201,
)
async def upload_document(
    organization_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    organization = db.get(Organization, organization_id)

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found.",
        )

    if len(file.filename or "") > 255:
        raise HTTPException(
            status_code=400,
            detail="Filename must be 255 characters or fewer.",
        )

    storage_path = await save_pdf(file)

    document = Document(
        organization_id=organization_id,
        filename=file.filename or "unnamed.pdf",
        content_type="application/pdf",
        storage_path=storage_path,
    )

    try:
        db.add(document)
        db.commit()
        db.refresh(document)
    except Exception:
        db.rollback()
        Path(storage_path).unlink(missing_ok=True)
        raise

    return {
        "id": document.id,
        "organization_id": document.organization_id,
        "filename": document.filename,
        "content_type": document.content_type,
        "created_at": document.created_at,
    }


@router.get("/organizations/{organization_id}/documents")
def list_documents(
    organization_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    organization = db.get(Organization, organization_id)

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found.",
        )

    statement = (
        select(Document)
        .where(Document.organization_id == organization_id)
        .order_by(Document.created_at.desc(), Document.id.desc())
    )

    documents = db.scalars(statement).all()

    return [
        {
            "id": document.id,
            "organization_id": document.organization_id,
            "filename": document.filename,
            "content_type": document.content_type,
            "created_at": document.created_at,
        }
        for document in documents
    ]

