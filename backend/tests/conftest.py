"""Pytest fixtures for database, client, and test data."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from app.db.session import get_session
from app.main import app


def pytest_addoption(parser):
    parser.addoption(
        "--db_mode",
        action="store",
        default="memory",
        help="Database mode: memory or file",
    )


@pytest.fixture(scope="session")
def engine(pytestconfig):
    db_mode = pytestconfig.getoption("db_mode")

    if db_mode == "memory":
        url = "sqlite:///:memory:"
        engine_args = {
            "connect_args": {"check_same_thread": False},
            # Use StaticPool for in-memory SQLite to avoid thread safety issues
            "poolclass": StaticPool,
        }
    else:
        url = "sqlite:///./test_tmp.db"
        engine_args = {
            "connect_args": {"check_same_thread": False},
        }
    return create_engine(url, **engine_args)


@pytest.fixture(scope="session")
def session_maker(engine):
    return sessionmaker(autoflush=False, autocommit=False, bind=engine)


# Creating a fixture db so we only have to create tables once
@pytest.fixture(scope="session")
def test_db(engine, session_maker):
    """In-memory SQLite database for each test."""
    SQLModel.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = session_maker(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(test_db):
    """FastAPI test client with test database."""

    # We must override the get_session dependency that returns the prod db
    def override_get_session():
        return test_db

    app.dependency_overrides[get_session] = override_get_session
    test_client = TestClient(app)
    return test_client


@pytest.fixture
def sample_user_data():
    """Sample user request data for testing."""
    return {"email": "test@example.com", "password": "testpass123"}
