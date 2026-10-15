import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import Organization


def get_organization(
    db: Session,
    organization_id: uuid.UUID,
) -> Organization | None:
    statement = select(Organization).where(Organization.id == organization_id)

    return db.scalars(statement).one_or_none()
