import uuid

from app.crud.organization import get_organization
from app.models.organization import Organization


def test_get_existing_organization(db_session):
    organization = Organization(name="KIP Test Organization")

    db_session.add(organization)
    db_session.flush()

    result = get_organization(db_session, organization.id)

    assert result is not None
    assert result.id == organization.id
    assert result.name == "KIP Test Organization"


def test_get_nonexistent_organization(db_session):
    nonexistent_id = uuid.uuid4()

    result = get_organization(db_session, nonexistent_id)

    assert result is None
