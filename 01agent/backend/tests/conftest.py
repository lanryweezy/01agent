import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool
from db.database import get_session
from main import app
from config.settings import Settings
import tempfile
import os

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def test_session(test_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    with Session(test_engine) as session:
        yield session

@pytest.fixture(scope="function")
def client(test_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with dependency overrides."""
    def get_test_session():
        yield test_session
    
    app.dependency_overrides[get_session] = get_test_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_settings():
    """Create test settings."""
    return Settings(
        environment="development",
        db_host="localhost",
        db_port=5432,
        db_database="test_db",
        db_username="test_user",
        db_password="test_password",
        jwt_secret="test-jwt-secret-key-for-testing-purposes-only",
        session_secret="test-session-secret-key-for-testing",
        allowed_hosts="localhost,127.0.0.1",
    )

@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "TestPassword123!"
    }

@pytest.fixture
def sample_login_data():
    """Sample login data for testing."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!"
    }

@pytest.fixture
def sample_thread_data():
    """Sample thread data for testing."""
    return {
        "task": "This is a test task for automation",
        "background_mode": False,
        "extended_thinking_mode": False
    }

class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_user_data(
        name: str = "Test User",
        email: str = "test@example.com",
        password: str = "TestPassword123!"
    ):
        return {
            "name": name,
            "email": email,
            "password": password
        }
    
    @staticmethod
    def create_thread_data(
        task: str = "Test automation task",
        background_mode: bool = False,
        extended_thinking_mode: bool = False
    ):
        return {
            "task": task,
            "background_mode": background_mode,
            "extended_thinking_mode": extended_thinking_mode
        }

@pytest.fixture
def test_data_factory():
    """Test data factory fixture."""
    return TestDataFactory