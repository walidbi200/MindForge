import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine

from ascend.infrastructure.database import get_session
from ascend.infrastructure.metadata import metadata
from ascend.main import app

# Use an in-memory SQLite database for testing
sqlite_url = "sqlite:///:memory:"
engine = create_engine(
    sqlite_url,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Create tables before tests run
    metadata.create_all(engine)
    yield
    # Drop tables after tests finish
    metadata.drop_all(engine)


@pytest.fixture
def db_session():
    # Provide a fresh session for each test
    with Session(engine) as session:
        yield session


@pytest.fixture
def test_client(db_session):
    def get_session_override():
        return db_session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
