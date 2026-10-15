import uuid

from fastapi.testclient import TestClient

from app.db.dependencies import get_db
from app.main import app
from app.models.organization import Organization


def test_read_existing_organization(db_session):
    organization = Organization(name="API Test Organization")
    db_session.add(organization)
    db_session.flush()

    app.dependency_overrides[get_db] = lambda: db_session

    try:
        with TestClient(app) as client:
            response = client.get(f"/api/v1/organizations/{organization.id}")

        assert response.status_code == 200
        assert response.json() == {
            "id": str(organization.id),
            "name": "API Test Organization",
        }
    finally:
        app.dependency_overrides.clear()


def test_read_nonexistent_organization(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        with TestClient(app) as client:
            response = client.get(f"/api/v1/organizations/{uuid.uuid4()}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Organization not found"
    finally:
        app.dependency_overrides.clear()


def test_read_invalid_organization_id(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/organizations/not-a-uuid")

        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()
