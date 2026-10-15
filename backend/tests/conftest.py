import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


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
