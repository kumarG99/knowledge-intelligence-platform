import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.organization import get_organization
from app.db.dependencies import get_db
from app.schemas.organization import OrganizationResponse

router = APIRouter(prefix="/organizations", tags=["Organizations"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get("/{organization_id}", response_model=OrganizationResponse)
def read_organization(organization_id: uuid.UUID, db: DbSession):
    organization = get_organization(db, organization_id)

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return organization
