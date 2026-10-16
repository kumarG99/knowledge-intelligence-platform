import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.session import get_db
from app.main import app


@pytest.fixture
def db_session():
    test_url = settings.test_database_url

    if not test_url:
        pytest.fail("TEST_DATABASE_URL is not configured")

    test_database = make_url(test_url)
    development_database = make_url(settings.database_url)

    if test_database.database != "kip_test_db":
        pytest.fail("Refusing to run tests outside kip_test_db")

    if test_database == development_database:
        pytest.fail("Test and development database URLs must differ")

    engine = create_engine(test_url, pool_pre_ping=True)

    connection = engine.connect()
    transaction = connection.begin()

    TestSessionLocal = sessionmaker(
        bind=connection,
        autoflush=False,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        engine.dispose()

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app, raise_server_exceptions=False) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)